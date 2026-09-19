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
    maintenance_request_ids = fields.One2many(
    'maintenance.request', 
    'lease_id', 
    string='Maintenance Requests'
)
    start_date = fields.Date(string='Start Date', required=True)
    end_date = fields.Date(string='End Date', required=True)
    monthly_rent = fields.Float(string='Monthly Rent', required=True)
    deposit_paid = fields.Float(string='Deposit Paid')
    booking_id = fields.Many2one('real_estate.booking', string='Booking Reference')
    user_id = fields.Many2one('res.users', string='Related User', index=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('at_risk', 'At Risk'),
        ('expired', 'Expired'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='draft', required=True)

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
        vals['name'] = self.env['ir.sequence'].next_by_code('real_estate.lease')
        return super(Lease, self).create(vals)


    def write(self, vals):
      if not self.env.user.has_group('real_estate.group_lease_manager'):
            raise UserError("You do not have permission to create a lease.")
      return super(Lease, self).write(vals)

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

    
