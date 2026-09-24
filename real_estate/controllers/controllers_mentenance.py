from odoo import http
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal

class MaintenancePortal(CustomerPortal):

    def _prepare_portal_layout_values(self):
        values = super(MaintenancePortal, self)._prepare_portal_layout_values()
        
        tenant = request.env['real_estate.tenant'].sudo().search([
            ('user_id', '=', request.env.user.id)
        ], limit=1)
        
        maintenance_count = 0
        if tenant:
            leases = request.env['real_estate.lease'].sudo().search([
                ('tenant_id', '=', tenant.id)
            ])
            maintenance_count = request.env['real_estate.maintenance_request'].sudo().search_count([
                ('lease_id', 'in', leases.ids)
            ])
            
        values.update({
            'maintenance_count': maintenance_count,
            'tenant': tenant,
        })
        return values

    @http.route(['/my/maintenance', '/my/maintenance/page/<int:page>'], type='http', auth='user', website=True)
    def portal_my_maintenance(self, page=1, **kw):
        values = self._prepare_portal_layout_values()
        tenant = values.get('tenant')
        
        if not tenant:
            values.update({'maintenance_requests': request.env['real_estate.maintenance_request'].sudo().browse()})
            return request.render('real_estate.portal_my_maintenance_requests', values)

        leases = request.env['real_estate.lease'].sudo().search([('tenant_id', '=', tenant.id)])
        maintenance_requests = request.env['real_estate.maintenance_request'].sudo().search([
            ('lease_id', 'in', leases.ids)
        ], order='create_date desc')

        values.update({
            'maintenance_requests': maintenance_requests,
            'page_name': 'maintenance',
        })
        return request.render('real_estate.portal_my_maintenance_requests', values)

    @http.route(['/my/maintenance/<int:maintenance_id>'], type='http', auth="user", website=True)
    def portal_maintenance_detail(self, maintenance_id, access_token=None, **kw):
        maintenance_req = request.env['real_estate.maintenance_request'].sudo().browse(maintenance_id)
        
        if not maintenance_req.exists():
            return request.not_found()
            
        values = {
            'maintenance_req': maintenance_req,
            'page_name': 'maintenance_detail',
        }
        return request.render("real_estate.portal_maintenance_page", values)