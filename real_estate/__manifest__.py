# -*- coding: utf-8 -*-
{
    'name': "real_estate",

    'summary': "Short (1 phrase/line) summary of the module's purpose",

    'description': """
Long description of module's purpose
    """,

    'author': "My Company",
    'website': "https://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',
    'license': 'LGPL-3',

    # any module necessary for this one to work correctly
    'depends': ['base', 'crm', 'portal', 'sale', 'mail'],

    # always loaded
    'data': [
        'security/category_security.xml',
        'security/property_security.xml',
        'security/ir.model.access.csv',
        'data/ir_sequence_data.xml',
        'wizard/lease_request.xml',
        'wizard/maintenance.xml',
        'wizard/booking.xml',
        'wizard/tenant.xml',
        'wizard/change_state_wizard_view.xml',
        'data/mail_template_data.xml',
        'report/property_report_templates.xml',
        'report/lease_report_templates.xml',
        'report/report.xml',          
        'views/views.xml',
        'views/portal_templates.xml',
        'views/portal_templates_mentenans.xml',
        'views/port_property.xml',
        'views/portal_payment.xml',
        'views/portal_tenant.xml',
        'views/templates.xml',
        'views/property_views.xml',    
         'views/inherit_res_partner.xml',            
        'views/inherit_sales.xml',
        # 'views/inherit_tenant.xml',
        'views/tenant.xml',
        'views/payments.xml',
        'views/lease_view.xml',
        'views/booking.xml',
        'views/maintenance_view.xml',
        'views/crm_lead_view.xml',
        'views/menu.xml',
        'wizard/lease_report_wizard_views.xml',
        'wizard/tenant_report_wizard_views.xml',
    ],

    # Assets configuration for styling
    'assets': {
        'web.assets_backend': [
    'real_estate/static/css/property.css',    
    ],
    },

    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}