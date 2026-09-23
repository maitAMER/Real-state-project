from odoo import http
from odoo.http import request
from werkzeug.urls import url_quote
from odoo.addons.portal.controllers.portal import CustomerPortal

class RealEstatePortal(CustomerPortal):

    def _prepare_portal_layout_values(self):
        values = super(RealEstatePortal, self)._prepare_portal_layout_values()
        
        property_count = request.env['real_estate.property'].sudo().search_count([
            ('agent_id', '=', request.env.user.id)
        ])

        values.update({
            'property_count': property_count,
        })
        return values

    @http.route(['/my/properties', '/my/properties/page/<int:page>'], type='http', auth='user', website=True)
    def portal_my_properties(self, page=1, **kw):
        values = self._prepare_portal_layout_values()
        
        properties = request.env['real_estate.property'].sudo().search([
            ('agent_id', '=', request.env.user.id)
        ], order='name desc')
        
        values.update({
            'properties': properties,
            'page_name': 'property',
        })
        return request.render('real_estate.portal_my_properties_template', values)
