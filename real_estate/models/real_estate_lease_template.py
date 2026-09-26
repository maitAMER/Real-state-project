from odoo import models, fields, api

class RealEstateLease(models.Model):
    _name = 'real_estate.lease'
    _inherit = ['real_estate.lease', 'mail.thread']
    _description = 'Property Lease Agreement'

    next_payment_date = fields.Date(string='Next Payment Date')
    last_reminder_sent = fields.Date(string='Last Reminder Sent', readonly=True)
    specialization = fields.Selection([
        ('residential', 'Residential'),
        ('commercial', 'Commercial'),
    ], string='Specialization')
    
  
    def send_reminder_email(self):
        template_xml_id = 'real_estate.email_template_payment_upcoming'
        if not template_xml_id:
            return
            
        template = self.env.ref(template_xml_id, raise_if_not_found=False)
        if not template:
            return

        for lease in self:
            if not lease.tenant_id.email:
                lease.message_post(body="Could not send reminder: Tenant has no email.")
                continue
            template.send_mail(lease.id, force_send=True)
            lease.last_reminder_sent = fields.Date.today()