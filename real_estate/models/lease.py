from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
from datetime import timedelta


class Lease(models.Model):
    _name = 'real_estate.lease'
    _description = 'Property Lease Agreement'

    name = fields.Char(string='Lease Reference', required=True, copy=False, readonly=True, default=lambda self: 'New')     

    property_id = fields.Many2one(
        'real_estate.property',  
        string='Property',
        required=True,
        ondelete='cascade',
        index=True
    )
    
    tenant_id = fields.Many2one(
        'real_estate.tenant',
        string='Tenant',
        required=True,
        ondelete='cascade',
        index=True
    )

    maintenance_request_ids = fields.One2many(
        'real_estate.maintenance_request',
        'lease_id',
        string='Maintenance Requests'
    )
    
    maintenance_request_count = fields.Integer(
        string='Maintenance Requests Count',
        compute='_compute_maintenance_request_count',
        store=False,
    )

    total_cost = fields.Float(
        compute='_compute_total_cost', string='Total Cost'
    )

    start_date = fields.Date(string='Start Date', required=True)
    end_date = fields.Date(string='End Date', required=True)
    payment_ids = fields.One2many('lease.payment', 'lease_id', string='Payments')
    monthly_rent = fields.Float(string='Monthly Rent', required=True)
    
    next_electrical_charge = fields.Date(
        string='Next Electrical Charge',
        compute='_compute_next_electrical_charge',
        store=True
    )
    
    deposit_paid = fields.Float(string='Deposit Paid')
    booking_id = fields.Many2one('real_estate.booking', string='Booking Reference')
    user_id = fields.Many2one('res.users', string='Related User', index=True)
    
    duration_months = fields.Integer(
        string='Duration (Months)', compute='_compute_duration', store=True
    )
    
    is_active = fields.Boolean(
        string='Currently Active', compute='_compute_is_active'
    )

    state = fields.Selection([
        ('active', 'Active'),  
        ('draft', 'Draft'),
        ('in_progress', 'In Progress'),
        ('expired', 'Expired'),
        ('done', 'Done'),
    ], default='draft', string='Status')

    @api.depends('maintenance_request_ids')
    def _compute_maintenance_request_count(self):
        for record in self:
            record.maintenance_request_count = len(record.maintenance_request_ids)

    def convert_to_active(self):
        if not self.env.user.has_group('real_estate.group_property_manager'):
            raise UserError("You do not have permission to activate a lease.")

        for record in self:
            record.write({'state': 'active'})

    def convert_to_draft(self):
        for record in self:
            record.write({'state': 'draft'})

    def unlink(self):
        if not self.env.user.has_group('real_estate.group_property_manager'):
            raise UserError("Only Property Managers can delete a lease.")
        return super().unlink()

    @api.model
    def create(self, vals):
        """Override create to generate lease reference"""
        if not vals.get('name') or vals.get('name') == 'New' or vals.get('name') == '/':
            vals['name'] = self.env['ir.sequence'].next_by_code('real_estate.lease') or 'New'
        return super(Lease, self).create(vals) 

    def action_maintenance_requests(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Maintenance Requests',
            'res_model': 'real_estate.maintenance_request',
            'view_mode': 'tree,form',
            'domain': [('lease_id', '=', self.id)],
            'context': {
                'default_lease_id': self.id,
                'default_property_id': self.property_id.id,
            },
        }

    def action_create_maintenance_request(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Create Maintenance Request',
            'res_model': 'maintenance.request.wizard',
            'view_mode': 'form',
            'target': 'new',
            'view_id': self.env.ref('real_estate.view_maintenance_request_wizard_form').id,
            'context': {
                'default_lease_id': self.id,
                'default_property_id': self.property_id.id,
            },
        }

    @api.depends('start_date', 'end_date')
    def _compute_duration(self):
        """Calculate lease duration in months"""
        for record in self:
            if record.start_date and record.end_date:
                delta = record.end_date - record.start_date
                record.duration_months = int(delta.days / 30)
            else:
                record.duration_months = 0

    @api.depends('start_date', 'end_date', 'state')
    def _compute_is_active(self):
        """Check if lease is currently active"""
        today = fields.Date.today()
        for record in self:
            if record.state == 'active' and record.start_date and record.end_date:
                record.is_active = record.start_date <= today <= record.end_date
            else:
                record.is_active = False

    @api.onchange('property_id')
    def _onchange_property_id(self):
        """Set default price when property is selected and validate availability"""
        if self.property_id and not self.property_id.available:
            raise ValidationError("The selected property is not available.")

        if self.property_id and self.property_id.price:
            self.monthly_rent = self.property_id.price
            self.deposit_paid = self.property_id.price * 0.10

    @api.depends('start_date')
    def _compute_next_electrical_charge(self):
        for record in self:
            if record.start_date:
                record.next_electrical_charge = record.start_date + timedelta(days=30)
            else:
                record.next_electrical_charge = False

    def action_create_electrical_charge_request(self):
        self.ensure_one()
        menten = self.env['real_estate.maintenance_request'].create({
            'lease_id': self.id,
            'issue_type': 'other',
            'description': 'Initial maintenance request',
            'scheduled_date': self.next_electrical_charge,
            'urgency': 'medium',
        })
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'real_estate.maintenance_request',
            'res_id': menten.id,
            'view_mode': 'form',
            'target': 'current',
        }

    # حقول محسوبة لتجميع التكاليف حسب نوع الصيانة
    plumbing_cost = fields.Float(string="Plumbing Cost", compute='_compute_maintenance_costs', store=True)
    electrical_cost = fields.Float(string="Electrical Cost", compute='_compute_maintenance_costs', store=True)
    air_condition_cost = fields.Float(string="Air Condition Cost", compute='_compute_maintenance_costs', store=True)
    appliance_cost = fields.Float(string="Appliance Cost", compute='_compute_maintenance_costs', store=True)
    other_cost = fields.Float(string="Other Cost", compute='_compute_maintenance_costs', store=True)
    
    total_cost = fields.Float(string="Total Cost", compute='_compute_maintenance_costs', store=True)

    @api.depends('maintenance_request_ids.actual_cost', 'maintenance_request_ids.issue_type')
    def _compute_maintenance_costs(self):
        for lease in self:
            plumbing = 0.0
            electrical = 0.0
            air_cond = 0.0
            appliance = 0.0
            other = 0.0

            for req in lease.maintenance_request_ids:
                cost = req.actual_cost or 0.0
                if req.issue_type == 'plumbing':
                    plumbing += cost
                elif req.issue_type == 'electrical':
                    electrical += cost
                elif req.issue_type == 'air_condition':
                    air_cond += cost
                elif req.issue_type == 'appliance':
                    appliance += cost
                else:
                    other += cost

            lease.plumbing_cost = plumbing
            lease.electrical_cost = electrical
            lease.air_condition_cost = air_cond
            lease.appliance_cost = appliance
            lease.other_cost = other
            lease.total_cost = plumbing + electrical + air_cond + appliance + other

    payment_count = fields.Integer(string='Payment Count', compute='_compute_payment_count')

    def _compute_payment_count(self):
        for lease in self:
            lease.payment_count = self.env['lease.payment'].search_count([('lease_id', '=', lease.id)])

    def action_open_payments(self):
        self.ensure_one()
        return {
            'name': 'Payments',
            'type': 'ir.actions.act_window',
            'res_model': 'lease.payment',
            'view_mode': 'tree,form',
            'domain': [('lease_id', '=', self.id)],
            'context': {'default_lease_id': self.id},
            'target': 'current',
        }

    total_cash_amount = fields.Float(string='Total Cash Amount', compute='_compute_payment_information', store=True)
    total_visa_amount = fields.Float(string='Total Visa Amount', compute='_compute_payment_information', store=True)
    total_payment_amount = fields.Float(string='Total Payments', compute='_compute_payment_information', store=True)

    @api.depends('payment_ids.amount', 'payment_ids.payment_method', 'payment_ids.state')
    def _compute_payment_information(self):
        for record in self:
            valid_payments = record.payment_ids.filtered(lambda p: p.state in ['paid', 'reconciled'])

            costs = {
                method: sum(
                    valid_payments.filtered(
                        lambda payment: payment.payment_method == method
                    ).mapped('amount')
                )
                for method in ['cash', 'check', 'bank_transfer', 'credit_card', 'other']
            }

            record.total_cash_amount = costs['cash']
            record.total_visa_amount = costs['credit_card']
            record.total_payment_amount = sum(costs.values())

    def _cron_auto_expire_leases(self):
        """Scheduled action - expire leases whose end date has passed"""
        today = fields.Date.today()
        expired_leases = self.search([
            ('end_date', '<', today),
        ])
        for lease in expired_leases:
            lease.write({'state': 'expired'})

    @api.constrains('deposit_paid', 'monthly_rent')
    def _check_deposit_amount(self):
        """Ensure deposit paid is less than monthly rent"""
        for record in self:
            if record.deposit_paid >= record.monthly_rent:
                raise ValidationError("Validation Error: Deposit Paid must be less than the Monthly Rent!")