from odoo import models, fields, api
from datetime import timedelta


class MaintenanceRequest(models.Model):
    _name = 'real_estate.maintenance_request'
    _description = 'Property Maintenance Request'

    name = fields.Char(string='Request Reference')
    lease_id = fields.Many2one('real_estate.lease', string='Lease')
    property_id = fields.Many2one(
        'real_estate.property',
        related='lease_id.property_id',
        store=True,
        readonly=True,
        string='Property'
    )
    tenant_phone = fields.Char(string='Tenant Phone')
    preferred_date = fields.Date(string='Preferred Date')
    state = fields.Selection([
        ('submitted', 'Submitted'),
        ('in_progress', 'In Progress'),
        ('done', 'Done'),
        ('cancelled', 'Cancelled'),
    ], default='new', string='status')

    issue_type = fields.Selection([
        ('plumbing', 'Plumbing'),
        ('electrical', 'Electrical'),
        ('air_condition', 'Air Condition'),
        ('appliance', 'Appliance'),
        ('other', 'Other')
    ], required=True)
    description = fields.Text(required=True)
    urgency = fields.Selection([
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('emergency', 'Emergency')
    ], default='medium', required=True)
    assigned_to = fields.Many2one('res.users', string='Assigned To')
    scheduled_date = fields.Date()
    completion_date = fields.Date()
    actual_cost = fields.Float()

    @api.model
    def create(self, vals):
        if not vals.get('assigned_to'):
            vals['assigned_to'] = self.env.user.id
        return super().create(vals)

    # Automation

    def _cron_auto_expire_leases(self):
        """Scheduled action - expire leases whose end date has passed"""
        today = fields.Date.today()
        expired_leases = self.search([
            ('end_date', '<', today),
        ])
        for lease in expired_leases:
            lease.write({'state': 'expired'})

         # Automation - Scheduled Action for Emergency Requests
    def _cron_auto_schedule_emergency(self):
        """Scheduled action - set scheduled_date to tomorrow if urgency is emergency"""
        tomorrow = fields.Date.today() + timedelta(days=1)
        emergency_requests = self.search([
            ('urgency', '=', 'emergency'),
            ('scheduled_date', '!=', tomorrow),
        ])
        for req in emergency_requests:
            req.write({'scheduled_date': tomorrow})