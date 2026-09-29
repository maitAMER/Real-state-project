import io
import xlsxwriter
from odoo import http
from odoo.exceptions import UserError
from odoo.http import request, content_disposition

class RealEstateController(http.Controller):
    
    @http.route('/real_estate/property/excel_export/<int:property_id>', type='http', auth='user')
    def property_excel_export(self, property_id, **kwargs):
        """
        Export single property details to Excel
        """
        property_obj = request.env['real_estate.property'].browse(property_id)
        
        if not property_obj.exists():
            return request.not_found()
        
        # Create Excel file in memory
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        
        # Add worksheet
        worksheet = workbook.add_worksheet('Property Details')
        
        # Define formats
        header_format = workbook.add_format({
            'bold': True,
            'bg_color': "#2B57A2",
            'font_color': 'white',
            'border': 1,
            'align': 'center',
            'valign': 'vcenter'
        })
        
        title_format = workbook.add_format({
            'bold': True,
            'font_size': 14,
            'align': 'left'
        })
        
        label_format = workbook.add_format({
            'bold': True,
            'bg_color': '#F2F2F2',
            'border': 1
        })
        
        data_format = workbook.add_format({
            'border': 1
        })
        
        currency_format = workbook.add_format({
            'num_format': '$#,##0.00',
            'border': 1
        })
        
        date_format = workbook.add_format({
            'num_format': 'yyyy-mm-dd',
            'border': 1
        })
        
        # Set column widths
        worksheet.set_column('A:A', 25)
        worksheet.set_column('B:B', 30)
        worksheet.set_column('C:E', 15)
        
        # Title
        row = 0
        worksheet.merge_range(row, 0, row, 1, f'Property Report: {property_obj.name}', title_format)
        row += 2

        header_format.set_bg_color("#6D82B6") 
        # Basic Information Section
        worksheet.merge_range(row, 0, row, 1, 'BASIC INFORMATION', header_format)
        row += 1
        
        property_data = [
            ('Property Name', property_obj.name),
            ('Property Type', dict(property_obj._fields['property_type'].selection).get(property_obj.property_type, '')),
            ('Status', 'Available' if property_obj.available else 'Occupied'),
            ('Agent', property_obj.agent_id.display_name or ''),
            ('Bedrooms', property_obj.bedrooms),
            ('Created By', property_obj.create_uid.display_name or ''),
            ('Price', property_obj.price),
        ]
        
        for label, value in property_data:
            worksheet.write(row, 0, label, label_format)
            worksheet.write(row, 1, value, data_format)
            row += 1
        
        row += 1
        
        # Pricing Section
        worksheet.merge_range(row, 0, row, 1, 'PRICING & REVENUE', header_format)
        row += 1
        
        worksheet.write(row, 0, 'Monthly Rent', label_format)
        worksheet.write(row, 1, property_obj.price, currency_format)
        row += 1
        
        worksheet.write(row, 0, 'Security Deposit', label_format)
        worksheet.write(row, 1, property_obj.deposit, currency_format)
        row += 1

        worksheet.write(row, 0, 'Monthly Revenue', label_format)
        monthly_revenue = sum(property_obj.lease_ids.filtered('is_active').mapped('monthly_rent'))
        worksheet.write(row, 1, monthly_revenue, currency_format)
        row += 1
        
        row += 2
        
        # Leases Table
        if property_obj.lease_ids:
            worksheet.merge_range(row, 0, row, 4, 'LEASE HISTORY', header_format)
            row += 1
            
            # Table headers
            headers = ['Tenant', 'Rent', 'Start Date', 'End Date', 'Status']
            for col, header in enumerate(headers):
                worksheet.write(row, col, header, header_format)
            row += 1
            
            # Table data
            for lease in property_obj.lease_ids.sorted(key=lambda r: r.start_date, reverse=True):
                worksheet.write(row, 0, lease.tenant_id.name or '', data_format)
                worksheet.write(row, 1, lease.monthly_rent, currency_format)
                worksheet.write(row, 2, lease.start_date or '', date_format)
                worksheet.write(row, 3, lease.end_date or '', date_format)
                worksheet.write(row, 4, dict(lease._fields['state'].selection).get(lease.state, ''), data_format)
                row += 1




        # Payment Information Section


        is_property_manager = request.env.user.has_group(
            'real_estate.group_property_manager'
        )
        if is_property_manager:
            payments = request.env['lease.payment'].search(
                [('property_id', '=', property_obj.id)],
                order='due_date desc, id desc',
            )

            if payments:
                row += 2
                payment_header_format = workbook.add_format({
                    'bold': True,
                    'bg_color': '#306BA7',
                    'font_color': 'white',
                    'border': 1,
                    'align': 'center',
                    'valign': 'vcenter',
                })
                worksheet.merge_range(row, 0, row, 3, 'PAYMENTS HISTORY', payment_header_format)
                row += 1

                payment_headers = ['Reference', 'Amount Due', 'Due Date', 'Payment Date']
                for col, header in enumerate(payment_headers):
                    worksheet.write(row, col, header, payment_header_format)
                row += 1

                for payment in payments:
                    worksheet.write(row, 0, payment.name or '', data_format)
                    worksheet.write(row, 1, payment.amount, currency_format)
                    worksheet.write(row, 2, payment.due_date or '', date_format)
                    worksheet.write(row, 3, payment.payment_date or '', date_format)
                    row += 1
        else:
            row += 2
            hidden_format = workbook.add_format({
                'bold': True,
                'bg_color': '#F2F2F2',
                'font_color': '#666666',
                'border': 1,
                'align': 'center',
                'valign': 'vcenter',
            })
            worksheet.merge_range(row, 0, row, 3, 'Payments data is hidden', hidden_format)

        # Close workbook
        workbook.close()
        
        # Prepare response
        output.seek(0)

        filename = f'Property_{property_obj.name.replace(" ", "_")}.xlsx'
        
        return request.make_response(
            output.read(),
            headers=[
                ('Content-Type', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'),
                ('Content-Disposition', content_disposition(filename))
            ]
        )