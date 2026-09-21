from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
from datetime import timedelta


class Lease(models.Model):
    _name = 'real_estate.lease'
    _description = 'Property Lease Agreement'

    name = fields.Char(string='lease Reference', required=True, copy=False)
    property_id = fields.Many2one(
        'real_estate.property',
        string='Property',
        required=True,
        ondelete='cascade',  # If property deleted, delete lease too
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

    total_cost = fields.Float(compute='_compute_total_coast', string='Total Cost')

    start_date = fields.Date(string='Start Date', required=True)
    end_date = fields.Date(string='End Date', required=True)
    monthly_rent = fields.Float(string='Monthly Rent', required=True)
    next_electrical_charge = fields.Date(
        string='Next Electrical Charge',
        compute='_compute_next_electrical_charge',
        store=True
    )
    deposit_paid = fields.Float(string='Deposit Paid')
    booking_id = fields.Many2one(
        'real_estate.booking', string='Booking Reference')
    user_id = fields.Many2one('res.users', string='Related User', index=True)
    duration_months = fields.Integer(
        string='Duration (Months)', compute='_compute_duration', store=True)
    is_active = fields.Boolean(
        string='Currently Active', compute='_compute_is_active')

    state = fields.Selection([
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('at_risk', 'At Risk'),
        ('expired', 'Expired'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='draft', required=True)

  # البحث في نموذج العقود عن الصيانه المرتبطة بهذا العقد
    @api.depends('maintenance_request_ids')
    def _compute_maintenance_request_count(self):
        for record in self:
            record.maintenance_request_count = len(
                record.maintenance_request_ids)

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
        # if vals.get('name', 'New') == 'New':
        vals['name'] = self.env['ir.sequence'].next_by_code(
            'real_estate.lease')
        return super(Lease, self).create(vals)

    def write(self, vals):
        if not self.env.user.has_group('real_estate.group_lease_manager'):
            raise UserError("You do not have permission to create a lease.")
        return super(Lease, self).write(vals)

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

   # علشان احسب الديوريشان

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

    @api.depends('start_date', 'end_date', 'state')
    def _compute_is_active(self):
        """Check if lease is currently active"""
        today = fields.Date.today()
        for record in self:
            if record.state == 'active' and record.start_date and record.end_date:
                record.is_active = record.start_date <= today <= record.end_date
            else:
                record.is_active = False

        # deposit 10%

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
                record.next_electrical_charge = record.start_date + \
                    timedelta(days=30)
            else:
                record.next_electrical_charge = False

    def action_create_electrical_charge_request(self):
        self.ensure_one()
        menten = self.env['real_estate.maintenance_request'].sudo().create({
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





    total_cost = fields.Float(compute='_compute_total_cost', string='Total Cost')

    @api.depends('maintenance_request_ids.actual_cost')
    def _compute_total_cost(self):
        for lease in self:
            # 1
             lease.total_cost = sum(maintenance.actual_cost for maintenance in lease.maintenance_request_ids)

    # totalcoast = fields.Integer(
    #         compute='compute_total_coast', string='total coast')
    # @api.depends('maintenance_request_ids.actual_cost')
    # def _compute_total_coast(self):
    #     lease.totalcoast=0
    #     for lease in self:
    #         total_cost = sum(
    #             request.actual_cost for request in lease.maintenance_request_ids)
    #         lease.totalcoast = total_cost

    # def action_open_maintenance_wizard(self):
    #     self.ensure_one()
    #     return {
    #         'type': 'ir.actions.act_window',
    #         'name': 'Maintenance Request',
    #         'res_model': 'maintenance.request.wizard',
    #         'view_mode': 'form',
    #         'target': 'new',
    #         'view_id': self.env.ref('real_estate.view_maintenance_request_wizard_form').id,
    #         'context': {
    #             'default_lease_id': self.id,
    #             'default_property_id': self.property_id.id,
    #         },
    #     }
