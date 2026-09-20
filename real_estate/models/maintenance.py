from odoo import models, fields, api

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
    ], default='submitted', required=True)

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
