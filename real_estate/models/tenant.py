# from my_adds.Real_state_project.real_estate.models import booking
from odoo import models, fields , api

class Tenant(models.Model):
    _name = 'real_estate.tenant'
    _description = 'Real Estate Tenant'
    _order = 'name asc'
    
    # === CORE FIELDS ===
    name = fields.Char(string='Tenant Name', required=True, index=True)
    email = fields.Char(string='Email', index=True)
    phone = fields.Char(string='Phone Number')
    mobile = fields.Char(string='Mobile Number')
    city = fields.Char(string='City')
    date_joined = fields.Date(string='Date Joined', default=fields.Date.today, readonly=True)
    date_of_birth = fields.Date(string='Date of Birth')
    notes = fields.Text(string='Notes')
    description = fields.Text(string='Description')
    # user_id = fields.Many2one('res.users', string='Related User', index=True)
    user_id = fields.Many2one('res.users', string='User', default=lambda self: self.env.user)
    lease_ids = fields.One2many(
        'real_estate.lease',
        'tenant_id',
        string='Leases'
    )
    lease_ids = fields.One2many(
        'real_estate.lease', 
        'property_id',          
        string="Leases"
    )
        
    lease_count = fields.Integer(
            string='Lease Count',
            compute='_compute_lease_count',
            store=False,
        )
        
    
    # class Tenant(models.Model):
    #  _name = 'real_estate.tenant'

    # phone = fields.Integer(string='Phone Number')
    # mobile = fields.Float(string='Mobile Number')
    


    # class Booking(models.Model):
    #  _name = 'real_estate.tenant.booking'

    # phone = fields.Integer(string='Age')
    # mobile = fields.Float(string='mobile')
    
    # user_id = fields.Many2one(
    #     'res.users',
    #     string='Related User',
    #     index=True,
    #     default=lambda self: self.env.user,
    # )


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

    @api.depends('lease_ids')
    def _compute_lease_count(self):
        for record in self:
            record.lease_count = len(record.lease_ids)

    def action_lease(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Leases',
            'res_model': 'real_estate.lease',
            'view_mode': 'tree,form',
            'domain': [('property_id', '=', self.id)],
            'context': {
                'default_property_id': self.id,
            },
        }


    @api.model
    def create(self, vals):
        """Generate a tenant sequence only when no name is provided."""
        if not vals.get('name'):
            vals['name'] = self.env['ir.sequence'].next_by_code('real_estate.tenant')
        return super(Tenant, self).create(vals)


