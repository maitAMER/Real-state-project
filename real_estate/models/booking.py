# from my_adds.Real_state_project.real_estate.models.lease import Lease
from odoo import models, fields , api

class booking(models.Model):
    _name = 'real_estate.booking'
    _description = 'Real Estate Booking & Inspection'

    name = fields.Char(string='Booking Reference', required=True, copy=False)
    agent_id = fields.Many2one('res.users', string='sales person')
    property_id = fields.Many2one('real_estate.property', string='Property', required=True)
    booking_date = fields.Datetime(string='Inspection/Booking Date', required=True, default=fields.Datetime.now)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('converted', 'Converted to Lease'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='draft', tracking=True)
    notes = fields.Text(string='Notes')


    def convert_to_draft(self):
        for record in self:
            record.write({'state': 'draft'})

    def convert_to_confirmed(self):
        for record in self:
            record.write({'state': 'confirmed'})

    def convert_to_converted(self):
        for record in self:
            record.write({'state': 'converted'})

    def convert_to_cancelled(self):
        for record in self:
            record.write({'state': 'cancelled'})


    @api.model
    def create(self, vals):
        """Override create to generate lease reference"""
        # if vals.get('name', 'New') == 'New':
        vals['name'] = self.env['ir.sequence'].next_by_code('real_estate.booking')
        return super(booking, self).create(vals)
    