# -*- coding: utf-8 -*-

import io
import base64
import xlsxwriter

from odoo import models, fields
from odoo.exceptions import UserError


class MaintenanceReportWizard(models.TransientModel):
    _name = 'maintenance.report.wizard'
    _description = 'Maintenance Report Wizard'

    date_from = fields.Date(
        string='Date From',
        required=True,
        default=fields.Date.today
    )

    date_to = fields.Date(
        string='Date To',
        required=True,
        default=fields.Date.today
    )

    # Optional report filter
    issue_type = fields.Selection(
        selection=[
            ('plumbing', 'Plumbing'),
            ('electrical', 'Electrical'),
            ('air_condition', 'Air Condition'),
            ('appliance', 'Appliance'),
            ('other', 'Other'),
        ],
        string='Issue Type',
        required=False
    )

    # Optional report filter
    urgency = fields.Selection(
        selection=[
            ('all', 'All'),
            ('low', 'Low'),
            ('medium', 'Medium'),
            ('high', 'High'),
            ('emergency', 'Emergency'),
        ],
        string='Urgency',
        default='all'
    )

    property_id = fields.Many2one(
        'real_estate.property',
        string='Property'
    )

    tenant_id = fields.Many2one(
        'real_estate.tenant',
        string='Tenant'
    )

    excel_file = fields.Binary(
        string='Excel File',
        readonly=True
    )

    excel_filename = fields.Char(
        string='Filename',
        readonly=True
    )

    def action_generate_report(self):
        self.ensure_one()

        if self.date_from > self.date_to:
            raise UserError(
                'Date From must be earlier than or equal to Date To.'
            )

        # اسم الموديل مطابق لتعريفه في models/maintenance.py
        Maintenance = self.env['real_estate.maintenance_request']
        # ---------------------------------------------------------
        # SEARCH DOMAIN
        # ---------------------------------------------------------

        domain = [
            '|',
            '&',
            ('preferred_date', '>=', self.date_from),
            ('preferred_date', '<=', self.date_to),
            '&',
            ('scheduled_date', '>=', self.date_from),
            ('scheduled_date', '<=', self.date_to),
        ]

        if self.issue_type:
            domain.append(
                ('issue_type', '=', self.issue_type)
            )

        # Urgency is optional
        if self.urgency and self.urgency != 'all':
            domain.append(
                ('urgency', '=', self.urgency)
            )

        # Maintenance can be filtered by property
        if self.property_id:
            domain.append(
                ('property_id', '=', self.property_id.id)
            )

        # Or by tenant
        if self.tenant_id:
            domain.append(
                ('tenant_id', '=', self.tenant_id.id)
            )

        maintenance_requests = Maintenance.search(
            domain,
            order='scheduled_date asc, id asc'
        )

        # ---------------------------------------------------------
        # EXCEL
        # ---------------------------------------------------------

        output = io.BytesIO()

        workbook = xlsxwriter.Workbook(
            output,
            {'in_memory': True}
        )

        # ---------------------------------------------------------
        # CALM LUXURY COLORS
        # ---------------------------------------------------------

        title_format = workbook.add_format({
            'bold': True,
            'font_size': 16,
            'font_color': '#4A4036',
            'bg_color': '#E8DCC8',
            'align': 'center',
            'valign': 'vcenter',
            'border': 1,
            'border_color': '#CFC0A8',
        })

        header_format = workbook.add_format({
            'bold': True,
            'font_color': '#4A4036',
            'bg_color': '#D8C7AA',
            'border': 1,
            'border_color': '#BDAE96',
            'align': 'center',
            'valign': 'vcenter',
            'text_wrap': True,
        })

        data_format = workbook.add_format({
            'bg_color': '#FBF8F2',
            'border': 1,
            'border_color': '#E2D9CA',
            'font_color': '#51483E',
        })

        date_format = workbook.add_format({
            'num_format': 'yyyy-mm-dd',
            'bg_color': '#FBF8F2',
            'border': 1,
            'border_color': '#E2D9CA',
            'font_color': '#51483E',
        })

        currency_format = workbook.add_format({
            'num_format': '#,##0.00',
            'bg_color': '#FBF8F2',
            'border': 1,
            'border_color': '#E2D9CA',
            'font_color': '#51483E',
        })

        summary_label_format = workbook.add_format({
            'bold': True,
            'bg_color': '#F1EADF',
            'font_color': '#4A4036',
            'border': 1,
            'border_color': '#D8CCBA',
        })

        summary_value_format = workbook.add_format({
            'bg_color': '#FBF8F2',
            'font_color': '#51483E',
            'border': 1,
            'border_color': '#E2D9CA',
        })

        grand_total_format = workbook.add_format({
            'bold': True,
            'font_size': 12,
            'bg_color': '#B7A58A',
            'font_color': '#FFFFFF',
            'num_format': '#,##0.00',
            'border': 2,
            'border_color': '#96846B',
        })

        worksheet = workbook.add_worksheet(
            'Maintenance Report'
        )

        worksheet.hide_gridlines(2)

        worksheet.set_column('A:A', 18)
        worksheet.set_column('B:B', 24)
        worksheet.set_column('C:C', 22)
        worksheet.set_column('D:D', 18)
        worksheet.set_column('E:E', 15)
        worksheet.set_column('F:F', 35)
        worksheet.set_column('G:G', 22)
        worksheet.set_column('H:I', 16)
        worksheet.set_column('J:J', 16)

        row = 0

        # ---------------------------------------------------------
        # TITLE
        # ---------------------------------------------------------

        worksheet.merge_range(
            row,
            0,
            row,
            9,
            f'Maintenance Report ({self.date_from} to {self.date_to})',
            title_format
        )

        worksheet.set_row(row, 30)

        row += 2

        # ---------------------------------------------------------
        # SELECTED FILTERS
        # ---------------------------------------------------------

        issue_labels = dict(
            Maintenance._fields['issue_type'].selection
        )

        urgency_labels = dict(
            Maintenance._fields['urgency'].selection
        )

        worksheet.write(
            row,
            0,
            'Issue Type:',
            summary_label_format
        )

        worksheet.write(
            row,
            1,
            issue_labels.get(
                self.issue_type,
                self.issue_type or 'All'
            ),
            summary_value_format
        )

        worksheet.write(
            row,
            2,
            'Urgency:',
            summary_label_format
        )

        worksheet.write(
            row,
            3,
            urgency_labels.get(
                self.urgency,
                'All'
            ),
            summary_value_format
        )

        row += 1

        if self.property_id:

            worksheet.write(
                row,
                0,
                'Property:',
                summary_label_format
            )

            worksheet.write(
                row,
                1,
                self.property_id.name,
                summary_value_format
            )

        if self.tenant_id:

            worksheet.write(
                row,
                2,
                'Tenant:',
                summary_label_format
            )

            worksheet.write(
                row,
                3,
                self.tenant_id.name,
                summary_value_format
            )

        row += 2

        # ---------------------------------------------------------
        # DETAILS TABLE
        # ---------------------------------------------------------

        headers = [
            'Maintenance Date',
            'Property',
            'Tenant',
            'Issue Type',
            'Urgency',
            'Assigned To',
            'Scheduled Date',
            'Completion Date',
            'Actual Cost',
        ]

        for col, header in enumerate(headers):

            worksheet.write(
                row,
                col,
                header,
                header_format
            )

        worksheet.set_row(row, 30)

        row += 1

        # ---------------------------------------------------------
        # REPORT DATA
        # ---------------------------------------------------------

        total_actual_cost = 0.0
        issue_totals = {
            issue_value: {'count': 0, 'cost': 0.0}
            for issue_value, _issue_label in issue_labels.items()
        }

        for maintenance in maintenance_requests:

            issue_label = issue_labels.get(
                maintenance.issue_type,
                maintenance.issue_type or ''
            )

            urgency_label = urgency_labels.get(
                maintenance.urgency,
                maintenance.urgency or ''
            )

            # Maintenance Date
            maintenance_date = (
                maintenance.preferred_date
                or maintenance.scheduled_date
            )

            if maintenance_date:

                worksheet.write_datetime(
                    row,
                    0,
                    fields.Datetime.to_datetime(
                        maintenance_date
                    ),
                    date_format
                )

            else:

                worksheet.write(
                    row,
                    0,
                    '',
                    data_format
                )

            # Property
            worksheet.write(
                row,
                1,
                maintenance.property_id.name or '',
                data_format
            )

            # Tenant
            worksheet.write(
                row,
                2,
                maintenance.tenant_id.name or '',
                data_format
            )

            # Issue Type
            worksheet.write(
                row,
                3,
                issue_label,
                data_format
            )

            # Urgency
            worksheet.write(
                row,
                4,
                urgency_label,
                data_format
            )

            # Assigned To
            worksheet.write(
                row,
                5,
                maintenance.assigned_to.name or '',
                data_format
            )

            # Scheduled Date
            if maintenance.scheduled_date:

                worksheet.write_datetime(
                    row,
                    6,
                    fields.Datetime.to_datetime(
                        maintenance.scheduled_date
                    ),
                    date_format
                )

            else:

                worksheet.write(
                    row,
                    6,
                    '',
                    data_format
                )

            # Completion Date
            if maintenance.completion_date:

                worksheet.write_datetime(
                    row,
                    7,
                    fields.Datetime.to_datetime(
                        maintenance.completion_date
                    ),
                    date_format
                )

            else:

                worksheet.write(
                    row,
                    7,
                    '',
                    data_format
                )

            # Actual Cost
            actual_cost = maintenance.actual_cost or 0.0
            issue_total = issue_totals[maintenance.issue_type]
            issue_total['count'] += 1
            issue_total['cost'] += actual_cost

            worksheet.write_number(
                row,
                8,
                actual_cost,
                currency_format
            )

            total_actual_cost += actual_cost

            row += 1

        # ---------------------------------------------------------
        # TOTAL ACTUAL COST
        # ---------------------------------------------------------

        worksheet.write(
            row,
            7,
            'TOTAL ACTUAL COST:',
            grand_total_format
        )

        worksheet.write_number(
            row,
            8,
            total_actual_cost,
            grand_total_format
        )

        row += 3

        worksheet.write(
            row,
            0,
            'REPORT SUMMARY',
            summary_label_format
        )
        worksheet.merge_range(
            row,
            1,
            row,
            3,
            '',
            summary_label_format
        )

        row += 1
        for col, header in enumerate([
            'Issue Type',
            'Number of Requests',
            'Total Actual Cost',
        ]):
            worksheet.write(row, col, header, header_format)

        row += 1
        issue_types_to_show = (
            [self.issue_type]
            if self.issue_type
            else list(issue_labels)
        )
        for issue_value in issue_types_to_show:
            issue_total = issue_totals[issue_value]
            worksheet.write(
                row,
                0,
                issue_labels[issue_value],
                data_format
            )
            worksheet.write_number(
                row,
                1,
                issue_total['count'],
                summary_value_format
            )
            worksheet.write_number(
                row,
                2,
                issue_total['cost'],
                currency_format
            )
            row += 1

        worksheet.write(row, 0, 'Grand Total', grand_total_format)
        worksheet.write_number(
            row,
            1,
            len(maintenance_requests),
            grand_total_format
        )
        worksheet.write_number(
            row,
            2,
            total_actual_cost,
            grand_total_format
        )

        # ---------------------------------------------------------
        # CLOSE
        # ---------------------------------------------------------

        workbook.close()

        output.seek(0)

        self.write({
            'excel_file': base64.b64encode(
                output.read()
            ),
            'excel_filename': (
                f'Maintenance_Report_'
                f'{self.date_from}_'
                f'{self.date_to}.xlsx'
            ),
        })

        return {
            'type': 'ir.actions.act_window',
            'name': 'Maintenance Report',
            'res_model': 'maintenance.report.wizard',
            'view_mode': 'form',
            'res_id': self.id,
            'views': [
                (
                    self.env.ref(
                        'real_estate.view_maintenance_report_wizard_form'
                    ).id,
                    'form'
                )
            ],
            'target': 'new',
        }