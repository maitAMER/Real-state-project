# from odoo import models


# class TenantProfile(models.Model):
#     _name = 'real_estate.tenant.profile'
#     _description = 'Tenant Profile'
#     _inherit = 'real_estate.tenant'


from odoo import models, fields


class TenantProfile(models.Model):

    _name = 'real_estate.tenant.profile'
    _description = 'Tenant Profile'

    profile_name = fields.Char(string='Profile Name')
    profile_email = fields.Char(string='Profile Email')
    profile_phone = fields.Char(string='Phone')