# from my_adds.Real_state_project.real_estate.models import booking
from odoo.exceptions import UserError, ValidationError
from odoo import models, fields, api, Command
from datetime import date, datetime


class Tenant(models.Model):
    _name = 'real_estate.tenant'
    _description = 'Real Estate Tenant'
    _order = 'name asc'

    profile_id = fields.Many2one(
        'real_estate.tenant.profile',
        string='Tenant Profile',
        ondelete='cascade',
    )

    # === CORE FIELDS ===
    name = fields.Char(string='Tenant Name', required=True, index=True)
    email = fields.Char(string='Email', index=True)
    phone = fields.Char(string='Phone Number')
    mobile = fields.Char(string='Mobile Number')
    city = fields.Char(string='City')
    date_joined = fields.Date(string='Date Joined',
                              default=fields.Date.today, readonly=True)
    date_of_birth = fields.Date(string='Date of Birth')
    company_type = fields.Selection(
    selection=[
        ('person', 'Individual'),
        ('company', 'Company')
    ],
    string='Company Type'
)
    notes = fields.Text(string='Notes')
    description = fields.Text(string='Description')
    # user_id = fields.Many2one('res.users', string='Related User', index=True)
    user_id = fields.Many2one('res.users', string='User', default=lambda self: self.env.user)
    age = fields.Integer(string='Age', compute='_compute_age', store=True)
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
    crm_id = fields.Many2one('crm.lead', string='CRM Lead')
    age_category = fields.Selection([
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


# البحث في نموذج التينانت عن العقود المرتبطة بهذا التينانت


    @api.depends('lease_ids')
    def _compute_lease_count(self):
        for record in self:
            record.lease_count = len(record.lease_ids)
# 2. دالة الانتقال عند الضغط على الزر

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

    @api.model_create_multi
    def create(self, vals_list):
        """Generate a tenant sequence only when no name is provided."""
        for vals in vals_list:
            if not vals.get('name'):
                vals['name'] = self.env['ir.sequence'].next_by_code(
                    'real_estate.tenant')
        return super().create(vals_list)

    @api.depends('date_of_birth')
    def _compute_age(self):
        today = fields.Date.today()

        for record in self:
            if record.date_of_birth:
                dob = fields.Date.from_string(record.date_of_birth)
                record.age = today.year - dob.year - \
                    ((today.month, today.day) < (dob.month, dob.day))
            else:
                record.age = 0

    # _inherits = {'real_estate.tenant.profile': 'profile_id'}





    #create_new_user_portal>>>>>>>>>>>>>
    @api.constrains('email')
    def _check_email_unique(self):
        for tenant in self.filtered('email'):
            duplicate = self.sudo().search_count([
                ('email', '=', tenant.email),
                ('id', '!=', tenant.id),
            ])
            if duplicate:
                raise ValidationError('Email must be unique; this email is already registered.')

    def action_create_portal_user(self):
        self.ensure_one()
        if not self.email:
            raise UserError("Please enter an email address first to create a portal user.")
        
        User = self.env['res.users'].sudo()
        user = User.search([('login', '=', self.email)], limit=1)

        if not user:
            portal_group = self.env.ref('base.group_portal')
            user = User.create({
                'name': self.name,
                'login': self.email,
                'email': self.email,
                'groups_id': [Command.link(portal_group.id)],
            })
   
        self.user_id = user.id
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Success',
                'message': 'Portal user created and linked successfully!',
                'type': 'success',
                'sticky': False,
            }
        }


