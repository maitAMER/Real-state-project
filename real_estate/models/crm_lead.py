from odoo import models, fields

class CrmLead(models.Model):
    _inherit = 'crm.lead'

    property_type = fields.Selection([
        ('apartment', 'Apartment'),
        ('house', 'House'),
        ('villa', 'Villa'),
        ('commercial', 'Commercial'),
    ], string='Property Type', required=True)
    monthly_rent = fields.Float(string='Monthly Rent', required=True)
    age_category= fields.Selection([
            ('a', '0-20'),
            ('b', '21-40'),
            ('c', '41-60'),
        ], string='Age Category')

    def write_leadname_text(self):
            """Write lead name  text into the notes field"""
            for record in self:
                record.write({'description': record.name})

    def action_open_hycall_wizard(self):
        self.ensure_one()
        return {
            'name': 'HyCall Wizard',
            'type': 'ir.actions.act_window',
            'res_model': 'real_estate.tenant.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_lead_id': self.id,
                'default_name': self.contact_name or self.name,
                'default_phone': self.phone,
                'default_mobile': self.mobile,
                'default_email': self.email_from,
            },
        }
                