import odoo
from odoo import http, fields
from odoo.http import request
import json
from functools import wraps

class RealEstateAPI(http.Controller):
    
    @http.route('/api/properties/create', type='json', auth='none', methods=['POST'], csrf=False)
    def create_property(self, **kwargs):
        TOKEN = 'cacb064fd72c08b445959768'
        authorization_token = request.httprequest.headers.get('Authorization', '')
        if authorization_token != f'Bearer {TOKEN}':
            return request.make_json_response({'status': 'error', 'message': 'Unauthorized'}, status=401)


        try:
            params = kwargs
            print(request.env.user.name)
            # if not request.env.user.has_group('real_estate.group_property_manager'):
            #     return {
            #         'status': 'error',
            #         'message': 'You do not have permission to create properties'
            #     }
            # Validate required fields
            if not params.get('name') or not params.get('price'):
                return {
                    'status': 'error',
                    'message': 'Name and price are required'
                }
            
            # Create property
            property_obj = request.env['real_estate.property'].sudo().create({
                'name': params.get('name'),
                'price': params.get('price'),
                'bedrooms': params.get('bedrooms', 0),
                'property_type': params.get('property_type', 'house'),
                'external_id': params.get('external_id'),
            })
            
            return {
                'status': 'success',
                'message': 'Property created successfully',
                'data': {
                    'property_id': property_obj.id,
                    'name': property_obj.name,
                    'external_id': property_obj.external_id
                }
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }



    @http.route('/api/tenants/create', type='json', auth='none', methods=['POST'], csrf=False)
    def create_tenant(self, **kwargs):
        TOKEN = 'cacb064fd72c08b445959768'
        authorization_token = request.httprequest.headers.get('Authorization', '')
        if authorization_token != f'Bearer {TOKEN}':
            return request.make_json_response({'status': 'error', 'message': 'Unauthorized'}, status=401)


        try:
            params = kwargs
            if not params.get('name') or not params.get('email'):
                return {
                    'status': 'error',
                    'message': 'Name and email are required'
                }

            tenant = request.env['real_estate.tenant'].sudo().create({
                'name': params['name'],
                'email': params['email'],
                'created_from_api': True,
            })

            return {
                'status': 'success',
                'message': 'Tenant created successfully',
                'data': {
                    'tenant_id': tenant.id,
                    'name': tenant.name,
                    'email': tenant.email,
                }
            }

        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }



    @http.route('/api/tenants/update', type='json', auth='none', methods=['POST'], csrf=False)
    def update_tenant(self, **kwargs):
        TOKEN = 'cacb064fd72c08b445959768'
        authorization_token = request.httprequest.headers.get('Authorization', '')
        if authorization_token != f'Bearer {TOKEN}':
            return request.make_json_response({'status': 'error', 'message': 'Unauthorized'}, status=401)


        try:
            params = kwargs
            tenant_id = params.get('id')
            phone = params.get('phone')

            if not tenant_id:
                return {
                    'status': 'error',
                    'message': 'Tenant ID is required'
                }
            if not phone:
                return {
                    'status': 'error',
                    'message': 'Phone is required'
                }

            tenant = request.env['real_estate.tenant'].sudo().browse(
                int(tenant_id)
            ).exists()
            if not tenant:
                return {
                    'status': 'error',
                    'message': 'Tenant not found'
                }
            if not tenant.active:
                return {
                    'status': 'error',
                    'message': "This tenant is not active; can't update phone number"
                }

            tenant.write({'phone': phone})

            return {
                'status': 'success',
                'message': 'Tenant phone updated successfully',
                'data': {
                    'tenant_id': tenant.id,
                    'phone': tenant.phone,
                }
            }
        except (TypeError, ValueError):
            return {
                'status': 'error',
                'message': 'Tenant ID must be a valid integer'
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }
 




     #Tenant_id_check

    @http.route('/api/tenants/<int:tenant_id>', type='http', auth='none', methods=['PUT'], csrf=False)
    def update_tenant(self, tenant_id):
        TOKEN = 'cacb064fd72c08b445959768'
        authorization_token = request.httprequest.headers.get('Authorization', '')
        if authorization_token != f'Bearer {TOKEN}':
            return request.make_json_response({'status': 'error', 'message': 'Unauthorized'}, status=401)


        tenant_obj = request.env['real_estate.tenant'].sudo().browse(tenant_id)
        # print(tenant_obj.name)
        if not tenant_obj.exists():
            return request.make_json_response(
                {'status': 'error', 
                 'message': 'Tenant not found'}, 
                 status=404
                 )
        
        params = request.httprequest.get_json(silent=True)

        tenant_obj.write(params)
        return request.make_json_response({'status': 'success', 
                                           'tenant_id': tenant_obj.id}
                                           )




      #property_id_check

    @http.route('/api/property/<int:property_id>', type='http', auth='none', methods=['PUT'], csrf=False)
    def update_property(self, property_id):
        TOKEN = 'cacb064fd72c08b445959768'
        authorization_token = request.httprequest.headers.get('Authorization', '')
        if authorization_token != f'Bearer {TOKEN}':
            return request.make_json_response({'status': 'error', 'message': 'Unauthorized'}, status=401)


        property_obj = request.env['real_estate.property'].sudo().browse(property_id)
        if not property_obj.exists():
            return request.make_json_response(
                {'status': 'error',
                 'message': 'Property not found'},
                status=404
                )

        params = request.httprequest.get_json(silent=True)
        property_obj.write(params)
        return request.make_json_response({'status': 'success',
        'property_id': property_obj.id}
)
      





    @http.route('/api/crm/create', type='json', auth='none', methods=['POST'], csrf=False)
    def create_crm_lead(self, **kwargs):
        TOKEN = 'cacb064fd72c08b445959768'
        authorization_token = request.httprequest.headers.get('Authorization', '')
        if authorization_token != f'Bearer {TOKEN}':
            return request.make_json_response({'status': 'error', 'message': 'Unauthorized'}, status=401)


        try:
            if not kwargs.get('name'):
                return {
                    'status': 'error',
                    'message': 'Lead name is required'
                }

            allowed_fields = (
                'contact_name', 'email_from', 'phone', 'mobile', 'description',
                'property_type', 'monthly_rent', 'age_category',
            )
            values = {'name': kwargs['name']}
            values.update({
                field: kwargs[field]
                for field in allowed_fields
                if field in kwargs
            })
            lead = request.env['crm.lead'].sudo().create(values)

            return {
                'status': 'success',
                'message': 'CRM lead created successfully',
                'data': {
                    'lead_id': lead.id,
                    'name': lead.name,
                    'email': lead.email_from,
                    'phone': lead.phone,
                    'property_type': lead.property_type,
                }
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }






    @http.route('/api/list_leases', type='http', auth='none', methods=['GET'], csrf=False)
    def list_leases(self):
        TOKEN = 'cacb064fd72c08b445959768'
        authorization_token = request.httprequest.headers.get('Authorization', '')
        if authorization_token != f'Bearer {TOKEN}':
          return request.make_json_response({'status': 'error', 'message': 'Unauthorized'}, status=401)


        date_from = request.httprequest.args.get('date_from')
        date_to = request.httprequest.args.get('date_to')
        if not date_from or not date_to:
            return request.make_json_response(
                {'status': 'error', 
                 'message': 'date_from and date_to are required'}, 
                 status=400
            )

        try:
            print('date_from 1:', date_from)
            date_from = fields.Date.to_date(date_from)
            date_to = fields.Date.to_date(date_to)
            print('date_from 2:', date_from)

        except Exception as e:
            return request.make_response(
                json.dumps({'status': 'error', 'message': str(e)}),
                headers={'Content-Type': 'application/json'}
            )

        if date_from > date_to:
            return request.make_response(
                json.dumps({'status': 'error', 
                            'message': 'date_from must be before date_to'}),
                headers={'Content-Type': 'application/json'}
            )

        leases = request.env['real_estate.lease'].sudo().search([
            ('start_date', '<=', date_to),
            ('end_date', '>=', date_from),
        ])
        return request.make_response(
            json.dumps({
                'status': 'success',
                'data': [{
                    'id': lease.id,
                    'name': lease.name,
                    'tenant': lease.tenant_id.name,
                    'property': lease.property_id.name,
                    'start_date': fields.Date.to_string(lease.start_date),
                    'end_date': fields.Date.to_string(lease.end_date),
                    'monthly_rent': lease.monthly_rent,
                    'state': lease.state,
                } for lease in leases],
            }),
            headers={'Content-Type': 'application/json'}


            
        )

    



    @http.route('/api/get_my_tenant', type='http', auth='none', methods=['GET'], csrf=False)
    def get_my_tenant(self ,tenant_id=None): 
        TOKEN = 'cacb064fd72c08b445959768'
        authorization_token = request.httprequest.headers.get('Authorization', '')
        if authorization_token != f'Bearer {TOKEN}':
            return request.make_json_response({'status': 'error', 'message': 'Unauthorized'}, status=401)

        tenant_id = request.httprequest.args.get('tenant_id')

        if not tenant_id:
            return request.make_json_response(
                {'status': 'error', 'message': 'tenant_id is required'},
                status=400,
            )

        try:
            tenant_id = int(tenant_id)
        except ValueError:
            return request.make_json_response(
                {'status': 'error', 'message': 'tenant_id must be an integer'},
                status=400,
            )

        leases = request.env['real_estate.lease'].sudo().search([
            ('tenant_id', '=', tenant_id),
        ])
        return request.make_json_response({
            'status': 'success',
            'data': [{
                'name': lease.name,
                'start_date': fields.Date.to_string(lease.start_date),
                'end_date': fields.Date.to_string(lease.end_date),
            } for lease in leases],
        })
    
    
    
    



    @http.route('/api/leases/create', type='json', auth='none', methods=['POST'], csrf=False)
    def create_lease(self, **kwargs):
        TOKEN = 'cacb064fd72c08b445959768'
        authorization_token = request.httprequest.headers.get('Authorization', '')
        if authorization_token != f'Bearer {TOKEN}':
            return request.make_json_response({'status': 'error', 'message': 'Unauthorized'}, status=401)


        try:
            params = kwargs
            tenant_data = params.get('tenant') or {}
            required_fields = (
                'property_id', 'start_date', 'end_date'
            )
            if (not tenant_data.get('name') or not tenant_data.get('email')
                    or any(params.get(field) in (None, '') for field in required_fields)):
                return {
                    'status': 'error',
                    'message': 'Tenant name, tenant email, property ID, start date, and end date are required'
                }

            tenant = request.env['real_estate.tenant'].sudo().create({
                'name': tenant_data['name'],
                'email': tenant_data['email'],
                'phone': tenant_data.get('phone'),
                'created_from_api': True,
            })

            lease = request.env['real_estate.lease'].sudo().create({
                'tenant_id': tenant.id,
                'property_id': params['property_id'],
                'start_date': params['start_date'],
                'end_date': params['end_date'],
            })
            
            return {
                'status': 'success',
                'message': 'Lease created successfully',
                'data': {
                    'lease_id': lease.id.name,
                    'tenant_id': tenant.id.name,
    
                }
            }

        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }


        







    




