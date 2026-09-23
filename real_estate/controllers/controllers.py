from odoo import http
from odoo.http import request
from werkzeug.urls import url_quote
from odoo.addons.portal.controllers.portal import CustomerPortal

class RealEstatePortal(CustomerPortal):

    def _prepare_portal_layout_values(self):
        values = super(RealEstatePortal, self)._prepare_portal_layout_values()
        tenant = request.env['real_estate.tenant'].sudo().search([
            ('user_id', '=', request.env.user.id)
        ], limit=1)
        lease_count = 0
        if tenant:
            lease_count = request.env['real_estate.lease'].sudo().search_count([
                ('tenant_id', '=', tenant.id)
            ])
        values.update({
            'lease_count': lease_count,
            'tenant': tenant,
        })
        return values

    @http.route(['/my/leases', '/my/leases/page/<int:page>'], type='http', auth='user', website=True)
    def portal_my_leases(self, page=1, **kw):
        values = self._prepare_portal_layout_values()
        tenant = values.get('tenant')
        if not tenant:
            values.update({
                'leases': request.env['real_estate.lease'].sudo().browse(),
            })
            return request.render('real_estate.portal_my_leases', values)

        leases = request.env['real_estate.lease'].sudo().search([
            ('tenant_id', '=', tenant.id),
            ('state', 'in', ['active'])
        ], order='start_date desc')
        values.update({
            'leases': leases,
        })
        return request.render('real_estate.portal_my_leases', values)