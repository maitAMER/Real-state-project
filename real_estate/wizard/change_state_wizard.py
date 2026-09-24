from odoo import fields, models

class ChangeState(models.TransientModel):
    _name = 'change.state'
    _description = 'Change State Wizard'

    # التصحيح هنا: ربطناها بالموديل الصح real_estate.property
    property_id = fields.Many2one('real_estate.property', string='Property')
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('pending', 'Pending')
    ], string='State', default='draft')
    
    reason = fields.Char(string='Reason')

    def action_confirm(self):
        print("inside confirm action")
        if self.property_id:
            self.property_id.state = self.state