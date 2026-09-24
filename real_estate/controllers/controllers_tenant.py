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

    # --- Tenant Profile Routes ---
    @http.route(['/my/account'], type='http', auth='user', website=True)
    def portal_my_account(self, **kw):
        values = self._prepare_portal_layout_values()
        values.update({'page_name': 'customer_account'})
        return request.render('real_estate.portal_my_account_template', values)

    @http.route(['/my/account/<int:tenant_id>'], type='http', auth='user', website=True)
    def portal_tenant_detail(self, tenant_id, **kw):
        tenant = request.env['real_estate.tenant'].sudo().search([
            ('id', '=', tenant_id),
            ('user_id', '=', request.env.user.id),
        ], limit=1)
        if not tenant:
            return request.not_found()
        values = self._prepare_portal_layout_values()
        values.update({
            'tenant': tenant,
            'page_name': 'customer_account_detail',
        })
        return request.render('real_estate.portal_tenant_detail_template', values)

    @http.route(['/my/account/update'], type='http', auth='user', methods=['POST'], website=True)
    def portal_my_account_update(self, **post):
        tenant = request.env['real_estate.tenant'].sudo().search([
            ('user_id', '=', request.env.user.id)
        ], limit=1)
        
        if tenant:
            tenant.sudo().write({
                'phone': post.get('phone'),
                'mobile': post.get('mobile'),
                'city': post.get('city'),
                'notes': post.get('notes'),
            })
        return request.redirect('/my/account/%s?success=1' % tenant.id if tenant else '/my/account')