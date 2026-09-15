from odoo import models, fields, api
from odoo.exceptions import UserError
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
    start_date = fields.Date(string='Start Date', required=True)
    end_date = fields.Date(string='End Date', required=True)
    monthly_rent = fields.Float(string='Monthly Rent', required=True)
    deposit_paid = fields.Float(string='Deposit Paid')
    booking_id = fields.Many2one('real_estate.booking', string='Booking Reference')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('at_risk', 'At Risk'),
        ('expired', 'Expired'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='draft', required=True)

    def convert_to_active(self):
        for record in self:
            record.write({'state': 'active'})


    def convert_to_draft(self):
        for record in self:
            record.write({'state': 'draft'})

    def unlink(self):
        raise UserError("You cannot delete a lease.")

    @api.model
    def create(self, vals):
        """Override create to generate lease reference"""
        # if vals.get('name', 'New') == 'New':
        vals['name'] = self.env['ir.sequence'].next_by_code('real_estate.lease')
        return super(Lease, self).create(vals)