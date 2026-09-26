from odoo import models, fields


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    test_field = fields.Char(string='Test Field')