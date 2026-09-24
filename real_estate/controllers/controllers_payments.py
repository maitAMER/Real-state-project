from odoo import http
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal

class PaymentPortal(CustomerPortal):

    def _prepare_portal_layout_values(self):
        values = super(PaymentPortal, self)._prepare_portal_layout_values()
        
        tenant = request.env['real_estate.tenant'].sudo().search([
            ('user_id', '=', request.env.user.id)
        ], limit=1)
        
        payment_count = 0
        if tenant:
            leases = request.env['real_estate.lease'].sudo().search([
                ('tenant_id', '=', tenant.id)
            ])
            payment_count = request.env['lease.payment'].sudo().search_count([
                ('lease_id', 'in', leases.ids)
            ])
            
        values.update({
            'payment_count': payment_count,
            'tenant': tenant,
        })
        return values

    @http.route(['/my/payments', '/my/payments/page/<int:page>'], type='http', auth='user', website=True)
    def portal_my_payments(self, page=1, **kw):
        values = self._prepare_portal_layout_values()
        tenant = values.get('tenant')
        
        if not tenant:
            values.update({'payments': request.env['lease.payment'].sudo().browse()})
            return request.render('real_estate.portal_my_payments_template', values)

        leases = request.env['real_estate.lease'].sudo().search([('tenant_id', '=', tenant.id)])
        payments = request.env['lease.payment'].sudo().search([
            ('lease_id', 'in', leases.ids)
        ], order='due_date desc')

        values.update({
            'payments': payments,
            'page_name': 'payment',
        })
        return request.render('real_estate.portal_my_payments_template', values)

    @http.route(['/my/payment/<int:payment_id>'], type='http', auth="user", website=True)
    def portal_payment_detail(self, payment_id, access_token=None, **kw):
        payment_record = request.env['lease.payment'].sudo().browse(payment_id)
        
        if not payment_record.exists():
            return request.not_found()
            
        values = {
            'payment_record': payment_record,
            'page_name': 'payment_detail',
        }
        return request.render("real_estate.portal_payment_page", values)