# from my_adds.Real_state_project.real_estate.models.booking import booking
from odoo import models, fields, api
from odoo.exceptions import UserError


class Property(models.Model):
    _name = 'real_estate.property'
    _description = 'Real Estate Property'

    name = fields.Char(string='Property Name', required=True, index=True)
    description = fields.Text(string='Description', default='Description')
    price = fields.Float(string='Monthly Rent', required=True)
    bedrooms = fields.Integer(string='Bedrooms')
    available = fields.Boolean(string='Available', default=True, index=True)
    agent_id = fields.Many2one('res.users', string='sales person')
    property_type = fields.Selection([
        ('apartment', 'Apartment'),
        ('house', 'House'),
        ('villa', 'Villa'),
        ('commercial', 'Commercial')
    ], string='Property Type')
    deposit = fields.Float(string='Deposit')

    state = fields.Selection([
        ('draft', 'Draft'),
        ('pending', 'Pending'),
        ('sold', 'Sold'),
        ('closed', 'Closed')
    ], string='Status', default='draft')

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

    _sql_constraints = [
        ('name_unique', 'unique(name)', 'Property name must be unique.')
    ]

    def mark_as_occupied(self):
        """Mark property as no longer available"""
        for record in self:
            record.write({'available': False, 'price': record.price + 1000})

    def mark_as_available(self):
        """Mark property as available"""
        for record in self:
            record.write({'available': True})

    def write_description_text(self):
        """Write default description text into the description field"""
        for record in self:
            record.write({'description': 'Description'})

    def write_agent_name_to_description(self):
        """Write the linked agent name into the description field"""
        for record in self:
            if record.agent_id:
                record.write({'description': record.agent_id.login})

    def Increase_deposit(self):
        """Increase the deposit amount"""
        for record in self:
            record.write({'deposit': record.deposit + 1000})

    def add_bedrooms(self):
        """Increase bedrooms by 1"""
        for record in self:
            record.write({'bedrooms': record.bedrooms + 1})

    def set_property_type_villa(self):
        """Set property_type to the villa selection key"""
        for record in self:
            if record.available:
                record.write({'property_type': 'villa'})

    def write(self, vals):
        for record in self:
            available = vals.get('available', record.available)
            if 'bedrooms' in vals and not available:
                raise UserError(
                    "You cannot edit the bedrooms "
                )
        return super(Property, self).write(vals)

    # دوال الـ State
    def action_pending(self):
        for record in self:
            record.state = 'pending'

    def action_sold(self):
        for record in self:
            record.state = 'sold'

    def action_closed(self):
        for record in self:
            record.state = 'closed'

    def action_draft(self):
        for record in self:
            record.state = 'draft'

    # دالة فتح الـ Wizard الجديدة
    def action_open_change_state_wizard(self):
        """Open the change state wizard"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Change State',
            'res_model': 'change.state',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_property_id': self.id,
            },
        }

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

    def action_print_property_summary(self):
        self.ensure_one()
        return self.env.ref('real_eastate.action_report_property_summary').report_action(self)