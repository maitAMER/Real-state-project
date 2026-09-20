# from my_adds.Real_state_project.real_estate.models.booking import booking
from odoo import models, fields, api
from odoo.addons.crm.populate.crm_lead import CrmLead
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



    lease_ids = fields.One2many(
    'real_estate.lease', 
    'property_id',          
    string="Leases"
)
    _sql_constraints = [
        ('name_unique', 'unique(name)', 'Property name must be unique.')]
    
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
                    "You cannot edit the  bedrooms "
                )
        return super(Property, self).write(vals)
    


    @api.model
    def create(self, vals):
            """Override create to generate lease reference"""
            # if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('real_estate.property')
            return super(Property, self).create(vals)


    # @api.model
    # def check_bedrooms_greater_zero(self):
    #     """Check if bedrooms is greater than 0"""
    #     for record in self:
    #         if record.bedrooms <= 0:
    #             raise UserError("Bedrooms must be greater than 0.")