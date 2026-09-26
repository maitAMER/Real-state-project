from odoo import models, fields, api
from odoo.exceptions import UserError
from datetime import timedelta


class LeasePayment(models.Model):
    _name = 'lease.payment'
    _description = 'Lease Payment'
    _order = 'due_date desc, id desc'

    name = fields.Char(string='Payment Reference', required=True,
                       copy=False, readonly=True, default='New')
    lease_id = fields.Many2one(
        'real_estate.lease', string='Lease', required=True, ondelete='cascade')
    tenant_id = fields.Many2one(
        related='lease_id.tenant_id', string='Tenant', store=True)
    property_id = fields.Many2one(
        related='lease_id.property_id', string='Property', store=True)

    due_date = fields.Date(string='Due Date', required=True)
    amount = fields.Float(string='Amount Due', required=True)
    late_fee = fields.Float(string='Late Fee')
    late_fee_applied = fields.Boolean(string='Late Fee Applied', default=False)
    total_amount = fields.Float(
        string='Total Amount', compute='_compute_total_amount', store=True)

    payment_date = fields.Date(string='Payment Date')
    payment_method = fields.Selection([
        ('cash', 'Cash'),
        ('check', 'Check'),
        ('bank_transfer', 'Bank Transfer'),
        ('credit_card', 'Credit Card'),
        ('other', 'Other')
    ], string='Payment Method')

    state = fields.Selection([
        ('draft', 'Draft'),
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('reconciled', 'Reconciled')
    ], default='draft', required=True)

    notes = fields.Text(string='Notes')

    @api.depends('amount', 'late_fee')
    def _compute_total_amount(self):
        for payment in self:
            payment.total_amount = payment.amount + payment.late_fee

    def action_pending(self):
        self.write({'state': 'pending'})

    def action_paid(self):
        self.write({
            'state': 'paid',
            'payment_date': fields.Date.today()
        })

    def action_reconciled(self):
        self.write({'state': 'reconciled'})

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code(
                    'lease.payment') or 'New'
        return super().create(vals_list)

    total_amount = fields.Float(
        string='Total Amount', compute='_compute_total_amount', store=True)

    @api.depends('amount', 'late_fee')
    def _compute_total_amount(self):
        for payment in self:
            payment.total_amount = payment.amount + payment.late_fee

    def action_open_lease(self):
        self.ensure_one()
        return {
            'name': 'Lease',
            'type': 'ir.actions.act_window',
            'res_model': 'real_estate.lease',
            'view_mode': 'form',
            'views': [(False, 'form')],
            'res_id': self.lease_id.id,
            'target': 'current',
        }



    def _cron_auto_mark_payments_as_paid(self):
        """Scheduled action - mark payments as paid"""
        payments_to_update = self.search([
            ('state', '!=', 'paid'),  
            ('amount', '=', 0.0), 
        ])
        
        for payment in payments_to_update:
            payment.write({'state': 'paid'})