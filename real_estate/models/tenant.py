# from my_adds.Real_state_project.real_estate.models import booking
from odoo import models, fields , api

class Tenant(models.Model):
    _name = 'real_estate.tenant'
    _description = 'Real Estate Tenant'
    _order = 'name asc'
    
    # === CORE FIELDS ===
    name = fields.Char(string='Tenant Name', required=True, index=True)
    email = fields.Char(string='Email', required=True, index=True)
    phone = fields.Char(string='Phone Number')
    mobile = fields.Char(string='Mobile Number')
    city = fields.Char(string='City')
    date_joined = fields.Date(string='Date Joined', default=fields.Date.today, readonly=True)
    date_of_birth = fields.Date(string='Date of Birth')
    notes = fields.Text(string='Notes')
    active = fields.Boolean(string='Active', default=True)
    crm_id=fields.Many2one('crm.lead', string='CRM Lead')
    age_category= fields.Selection([
            ('a', '0-20'),
            ('b', '21-40'),
            ('c', '41-60'),
        ], string='Age Category')

    def set_name_in_notes(self):
        """Write the tenant name into the notes field"""
        for record in self:
            if record.notes:
                record.notes += '\n' + record.name
            else:
                record.notes = record.name

 
    def add_crm_lead_name_to_notes(self):
             for record in self:
              if record.crm_id.email_from:
               record.write({'notes': record.crm_id.email_from}) 
             else:
              record.write({'notes': record.crm_id.website})

    @api.model
    def create(self, vals):
        """Override create to generate lease reference"""
        # if vals.get('name', 'New') == 'New':
        vals['name'] = self.env['ir.sequence'].next_by_code('real_estate.tenant')
        return super(Tenant, self).create(vals)