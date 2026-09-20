from odoo import fields, models


class BookingWizard(models.TransientModel):
    _name = 'real_estate.booking.wizard'
    _description = 'Booking Wizard'

    name = fields.Char(string='Booking Reference', required=True, default='New')
    property_id = fields.Many2one('real_estate.property', string='Property', required=True)
    agent_id = fields.Many2one('res.users', string='Sales Person')
    booking_date = fields.Datetime(string='Inspection/Booking Date', required=True, default=fields.Datetime.now)
    user_id = fields.Many2one('res.users', string='Related User', default=lambda self: self.env.user)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('converted', 'Converted to Lease'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='draft')
    notes = fields.Text(string='Notes')

    def action_create_lease(self):
        self.ensure_one()
        booking = self.env['real_estate.booking'].create({
            'name': self.name,
            'agent_id': self.agent_id.id,
            'property_id': self.property_id.id,
            'booking_date': self.booking_date,
            'user_id': self.user_id.id,
            'state': 'confirmed',
            'notes': self.notes,
        })
        self.state = 'converted'
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'real_estate.booking',
            'res_id': booking.id,
            'view_mode': 'form',
            'target': 'current',
        }
