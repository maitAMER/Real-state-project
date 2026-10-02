import odoo
from odoo import http, fields
from odoo.http import request
import json
from functools import wraps


# =========================
# API Response Helpers
# =========================

def valid_response(data=None, message='Success', status=200):
    return request.make_json_response({
        'status': 'success',
        'message': message,
        'data': data
    }, status=status)


def invalid_response(message='Bad Request', status=400, data=None):
    return request.make_json_response({
        'status': 'error',
        'message': message,
        'data': data
    }, status=status)


class RealEstateAPI(http.Controller):


    # ============================================================
    # 1. CREATE PROPERTY
    # Creates a new property in Odoo.
    # Required: name, price
    # ============================================================

    @http.route(
        '/api/properties/create',
        type='json',
        auth='none',
        methods=['POST'],
        csrf=False
    )
    def create_property(self, **kwargs):

        TOKEN = 'cacb064fd72c08b445959768'

        authorization_token = request.httprequest.headers.get(
            'Authorization', ''
        )

        if authorization_token != f'Bearer {TOKEN}':
            return invalid_response(
                message='Unauthorized',
                status=401
            )

        try:
            params = kwargs

            print(request.env.user.name)

            # Validate required fields
            if not params.get('name') or not params.get('price'):
                return invalid_response(
                    message='Name and price are required',
                    status=400
                )

            # Create property
            property_obj = request.env[
                'real_estate.property'
            ].sudo().create({
                'name': params.get('name'),
                'price': params.get('price'),
                'bedrooms': params.get('bedrooms', 0),
                'property_type': params.get(
                    'property_type',
                    'house'
                ),
                'external_id': params.get('external_id'),
            })

            return valid_response(
                message='Property created successfully',
                data={
                    'property_id': property_obj.id,
                    'name': property_obj.name,
                    'external_id': property_obj.external_id
                }
            )

        except Exception as e:
            return invalid_response(
                message=str(e),
                status=500
            )


    # ============================================================
    # 2. CREATE TENANT
    # Creates a new tenant in Odoo.
    # Required: name, email
    # ============================================================

    @http.route(
        '/api/tenants/create',
        type='json',
        auth='none',
        methods=['POST'],
        csrf=False
    )
    def create_tenant(self, **kwargs):

        TOKEN = 'cacb064fd72c08b445959768'

        authorization_token = request.httprequest.headers.get(
            'Authorization', ''
        )

        if authorization_token != f'Bearer {TOKEN}':
            return invalid_response(
                message='Unauthorized',
                status=401
            )

        try:
            params = kwargs

            if not params.get('name') or not params.get('email'):
                return invalid_response(
                    message='Name and email are required',
                    status=400
                )

            tenant = request.env[
                'real_estate.tenant'
            ].sudo().create({
                'name': params['name'],
                'email': params['email'],
                'created_from_api': True,
            })

            return valid_response(
                message='Tenant created successfully',
                data={
                    'tenant_id': tenant.id,
                    'name': tenant.name,
                    'email': tenant.email,
                }
            )

        except Exception as e:
            return invalid_response(
                message=str(e),
                status=500
            )


    # ============================================================
    # 3. UPDATE TENANT PHONE
    # Updates the phone number of an existing tenant.
    # Required: tenant ID, phone
    # ============================================================

    @http.route(
        '/api/tenants/update',
        type='json',
        auth='none',
        methods=['POST'],
        csrf=False
    )
    def update_tenant_phone(self, **kwargs):

        TOKEN = 'cacb064fd72c08b445959768'

        authorization_token = request.httprequest.headers.get(
            'Authorization', ''
        )

        if authorization_token != f'Bearer {TOKEN}':
            return invalid_response(
                message='Unauthorized',
                status=401
            )

        try:
            params = kwargs

            tenant_id = params.get('id')
            phone = params.get('phone')

            if not tenant_id:
                return invalid_response(
                    message='Tenant ID is required',
                    status=400
                )

            if not phone:
                return invalid_response(
                    message='Phone is required',
                    status=400
                )

            tenant = request.env[
                'real_estate.tenant'
            ].sudo().browse(
                int(tenant_id)
            ).exists()

            if not tenant:
                return invalid_response(
                    message='Tenant not found',
                    status=404
                )

            if not tenant.active:
                return invalid_response(
                    message="This tenant is not active; can't update phone number",
                    status=400
                )

            tenant.write({
                'phone': phone
            })

            return valid_response(
                message='Tenant phone updated successfully',
                data={
                    'tenant_id': tenant.id,
                    'phone': tenant.phone,
                }
            )

        except (TypeError, ValueError):
            return invalid_response(
                message='Tenant ID must be a valid integer',
                status=400
            )

        except Exception as e:
            return invalid_response(
                message=str(e),
                status=500
            )


    # ============================================================
    # 4. UPDATE TENANT BY ID
    # Updates tenant information using the tenant ID in the URL.
    # Method: PUT
    # ============================================================

    @http.route(
        '/api/tenants/<int:tenant_id>',
        type='http',
        auth='none',
        methods=['PUT'],
        csrf=False
    )
    def update_tenant_by_id(self, tenant_id):

        TOKEN = 'cacb064fd72c08b445959768'

        authorization_token = request.httprequest.headers.get(
            'Authorization', ''
        )

        if authorization_token != f'Bearer {TOKEN}':
            return invalid_response(
                message='Unauthorized',
                status=401
            )

        tenant_obj = request.env[
            'real_estate.tenant'
        ].sudo().browse(tenant_id)

        if not tenant_obj.exists():
            return invalid_response(
                message='Tenant not found',
                status=404
            )

        params = request.httprequest.get_json(silent=True)

        tenant_obj.write(params)

        return valid_response(
            message='Tenant updated successfully',
            data={
                'tenant_id': tenant_obj.id
            }
        )


    # ============================================================
    # 5. UPDATE PROPERTY BY ID
    # Updates property information using the property ID in the URL.
    # Method: PUT
    # ============================================================

    @http.route(
        '/api/property/<int:property_id>',
        type='http',
        auth='none',
        methods=['PUT'],
        csrf=False
    )
    def update_property(self, property_id):

        TOKEN = 'cacb064fd72c08b445959768'

        authorization_token = request.httprequest.headers.get(
            'Authorization', ''
        )

        if authorization_token != f'Bearer {TOKEN}':
            return invalid_response(
                message='Unauthorized',
                status=401
            )

        property_obj = request.env[
            'real_estate.property'
        ].sudo().browse(property_id)

        if not property_obj.exists():
            return invalid_response(
                message='Property not found',
                status=404
            )

        params = request.httprequest.get_json(silent=True)

        property_obj.write(params)

        return valid_response(
            message='Property updated successfully',
            data={
                'property_id': property_obj.id
            }
        )


    # ============================================================
    # 6. CREATE CRM LEAD
    # Creates a new CRM lead.
    # Required: name
    # ============================================================

    @http.route(
        '/api/crm/create',
        type='json',
        auth='none',
        methods=['POST'],
        csrf=False
    )
    def create_crm_lead(self, **kwargs):

        TOKEN = 'cacb064fd72c08b445959768'

        authorization_token = request.httprequest.headers.get(
            'Authorization', ''
        )

        if authorization_token != f'Bearer {TOKEN}':
            return invalid_response(
                message='Unauthorized',
                status=401
            )

        try:

            if not kwargs.get('name'):
                return invalid_response(
                    message='Lead name is required',
                    status=400
                )

            allowed_fields = (
                'contact_name',
                'email_from',
                'phone',
                'mobile',
                'description',
                'property_type',
                'monthly_rent',
                'age_category',
            )

            values = {
                'name': kwargs['name']
            }

            values.update({
                field: kwargs[field]
                for field in allowed_fields
                if field in kwargs
            })

            lead = request.env[
                'crm.lead'
            ].sudo().create(values)

            return valid_response(
                message='CRM lead created successfully',
                data={
                    'lead_id': lead.id,
                    'name': lead.name,
                    'email': lead.email_from,
                    'phone': lead.phone,
                    'property_type': lead.property_type,
                }
            )

        except Exception as e:
            return invalid_response(
                message=str(e),
                status=500
            )


    # ============================================================
    # 7. LIST LEASES
    # Returns all leases that overlap with the given date range.
    # Required query parameters: date_from, date_to
    # Method: GET
    # ============================================================

    @http.route(
        '/api/list_leases',
        type='http',
        auth='none',
        methods=['GET'],
        csrf=False
    )
    def list_leases(self):

        TOKEN = 'cacb064fd72c08b445959768'

        authorization_token = request.httprequest.headers.get(
            'Authorization', ''
        )

        if authorization_token != f'Bearer {TOKEN}':
            return invalid_response(
                message='Unauthorized',
                status=401
            )

        date_from = request.httprequest.args.get('date_from')
        date_to = request.httprequest.args.get('date_to')

        if not date_from or not date_to:
            return invalid_response(
                message='date_from and date_to are required',
                status=400
            )

        try:

            print('date_from 1:', date_from)

            date_from = fields.Date.to_date(date_from)
            date_to = fields.Date.to_date(date_to)

            print('date_from 2:', date_from)

        except Exception as e:
            return invalid_response(
                message=str(e),
                status=400
            )

        if date_from > date_to:
            return invalid_response(
                message='date_from must be before date_to',
                status=400
            )

        leases = request.env[
            'real_estate.lease'
        ].sudo().search([
            ('start_date', '<=', date_to),
            ('end_date', '>=', date_from),
        ])

        return valid_response(
            message='Leases retrieved successfully',
            data=[{
                'id': lease.id,
                'name': lease.name,
                'tenant': lease.tenant_id.name,
                'property': lease.property_id.name,
                'start_date': fields.Date.to_string(
                    lease.start_date
                ),
                'end_date': fields.Date.to_string(
                    lease.end_date
                ),
                'monthly_rent': lease.monthly_rent,
                'state': lease.state,
            } for lease in leases]
        )


    # ============================================================
    # 8. GET TENANT LEASES
    # Returns all leases belonging to a specific tenant.
    # Required query parameter: tenant_id
    # Method: GET
    # ============================================================

    @http.route(
        '/api/get_my_tenant',
        type='http',
        auth='none',
        methods=['GET'],
        csrf=False
    )
    def get_my_tenant(self, tenant_id=None):

        TOKEN = 'cacb064fd72c08b445959768'

        authorization_token = request.httprequest.headers.get(
            'Authorization', ''
        )

        if authorization_token != f'Bearer {TOKEN}':
            return invalid_response(
                message='Unauthorized',
                status=401
            )

        tenant_id = request.httprequest.args.get('tenant_id')

        if not tenant_id:
            return invalid_response(
                message='tenant_id is required',
                status=400
            )

        try:
            tenant_id = int(tenant_id)

        except ValueError:
            return invalid_response(
                message='tenant_id must be an integer',
                status=400
            )

        leases = request.env[
            'real_estate.lease'
        ].sudo().search([
            ('tenant_id', '=', tenant_id),
        ])

        return valid_response(
            message='Tenant leases retrieved successfully',
            data=[{
                'name': lease.name,
                'start_date': fields.Date.to_string(
                    lease.start_date
                ),
                'end_date': fields.Date.to_string(
                    lease.end_date
                ),
            } for lease in leases]
        )


    # ============================================================
    # 9. CREATE LEASE
    # Creates a new tenant and lease together.
    # Required:
    # tenant.name, tenant.email,
    # property_id, start_date, end_date
    # ============================================================

    @http.route(
        '/api/leases/create',
        type='json',
        auth='none',
        methods=['POST'],
        csrf=False
    )
    def create_lease(self, **kwargs):

        TOKEN = 'cacb064fd72c08b445959768'

        authorization_token = request.httprequest.headers.get(
            'Authorization', ''
        )

        if authorization_token != f'Bearer {TOKEN}':
            return invalid_response(
                message='Unauthorized',
                status=401
            )

        try:

            params = kwargs

            tenant_data = params.get('tenant') or {}

            if not isinstance(tenant_data, dict):
                return invalid_response(
                    message='Tenant must be an object',
                    status=400
                )

            required_fields = (
                'property_id',
                'start_date',
                'end_date'
            )

            if (
                not tenant_data.get('name')
                or not tenant_data.get('email')
                or any(
                    params.get(field) in (None, '')
                    for field in required_fields
                )
            ):
                return invalid_response(
                    message=(
                        'Tenant name, tenant email, property ID, '
                        'start date, and end date are required'
                    ),
                    status=400
                )

            with request.env.cr.savepoint():

                tenant = request.env[
                    'real_estate.tenant'
                ].sudo().create({
                    'name': tenant_data['name'],
                    'email': tenant_data['email'],
                    'phone': tenant_data.get('phone'),
                    'created_from_api': True,
                })

                lease = request.env[
                    'real_estate.lease'
                ].sudo().create({
                    'tenant_id': tenant.id,
                    'property_id': params['property_id'],
                    'start_date': params['start_date'],
                    'end_date': params['end_date'],
                })

            return valid_response(
                message='Lease created successfully',
                data={
                    'lease_id': lease.id,
                    'lease_reference': lease.name,
                    'tenant_id': tenant.id,
                }
            )

        except Exception as e:
            return invalid_response(
                message=str(e),
                status=500
            )



    @http.route(
    '/api/test_session',
    type='http',
    auth='user',
    methods=['GET'],
    csrf=False
)
    def test_session(self):
     return request.make_json_response({
        'status': 'success',
        'user_id': request.env.user.id,
        'user_name': request.env.user.name,
    })
    
    




    
     # valid_key

    @http.route(
        '/api/check_api_key',
        type='http',
        auth='none',
        methods=['GET'],
        csrf=False
    )
    def check_api_key(self):

        api_key = request.httprequest.headers.get(
            'Authorization',
            ''
        )

        api_key = api_key.replace('Bearer ', '').strip()

        user_id = request.env['res.users.apikeys']._check_credentials(
            scope='rpc',
            key=api_key
        )

        if not user_id:
            return invalid_response(
                message='Invalid API Key',
                status=401
            )

        return valid_response(
            message='Valid API Key',
            data={
                'user_id': user_id
            }
        )

