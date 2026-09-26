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

    @http.route(['/my/property/<int:property_id>'], type='http', auth="user", website=True)
    def portal_property_detail(self, property_id, access_token=None, **kw):
        property_record = request.env['real_estate.property'].sudo().browse(property_id)
        
        if not property_record.exists():
            return request.not_found()
            
        values = {
            'property_record': property_record,
            'page_name': 'property_detail',
        }
        return request.render("real_estate.portal_property_page", values)


class PublicPropertyWebsite(http.Controller):

    @http.route(['/', '/properties', '/properties/page/<int:page>'], type='http', auth="public", website=True)
    def public_property_list(self, search_type=None, min_price=None, max_price=None, min_bedrooms=None, **kwargs):
        domain = []
        
        if search_type:
            domain.append(('property_type', 'ilike', search_type))
        if min_price:
            domain.append(('price', '>=', float(min_price)))
        if max_price:
            domain.append(('price', '<=', float(max_price)))
        if min_bedrooms:
            domain.append(('bedrooms', '>=', int(min_bedrooms)))

        properties = request.env['real_estate.property'].sudo().search(domain, order='name desc')
        
        values = {
            'properties': properties,
            'search_type': search_type,
            'min_price': min_price,
            'max_price': max_price,
            'min_bedrooms': min_bedrooms,
        }
        return request.render("real_estate.property_list_template", values)