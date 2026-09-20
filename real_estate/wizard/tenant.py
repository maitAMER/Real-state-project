from odoo import api, fields, models


class TenantWizard(models.TransientModel):
    _name = 'real_estate.tenant.wizard'
    _description = 'Tenant Wizard'

    lead_id = fields.Many2one('crm.lead', string='Lead')
    name = fields.Char(string='Name')
    phone = fields.Char(string='Phone')
    mobile = fields.Char(string='Mobile')
    email = fields.Char(string='Email')

    # @api.model
    # def default_get(self, fields_list):
    #     res = super().default_get(fields_list)
    #     lead_id = self.env.context.get('active_id') or self.env.context.get('default_lead_id')
    #     if lead_id:
    #         lead = self.env['crm.lead'].browse(lead_id)
    #         if lead:
    #             res.update({
    #                 'lead_id': lead.id,
    #                 'name': lead.contact_name or lead.name,
    #                 'phone': lead.phone,
    #                 'mobile': lead.mobile,
    #                 'email': lead.email_from,
    #             })
    #     return res

    def action_create_tenant(self):
        self.ensure_one()
        vals = {
            'name': self.name or self.env['ir.sequence'].next_by_code('real_estate.tenant'),
            'phone': self.phone,
            'mobile': self.mobile,
            'email': self.email or False,
            'crm_id': self.lead_id.id if self.lead_id else False,
        }
        tenant = self.env['real_estate.tenant'].sudo().create(vals)
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'real_estate.tenant',
            'res_id': tenant.id,
            'views': [(False, 'form')],
            'target': 'current',
        }

