# -*- coding: utf-8 -*-
from odoo import api, models
from datetime import datetime, timedelta

class PropertyReportSummary(models.AbstractModel):
    _name = 'report.real_estate.report_property_summary'
    _description = 'Property Summary Report'
    
    @api.model
    def _get_report_values(self, docids, data=None):
        """
        Override to add custom data to report context
        """
        properties = self.env['real_estate.property'].browse(docids)
        
        # Calculate occupancy rate across all properties, not only the printed records.
        all_properties = self.env['real_estate.property'].search([])
        total_properties = len(all_properties)
        occupied = len(all_properties.filtered(lambda p: not p.available))
        occupancy_rate = (occupied / total_properties * 100) if total_properties else 0.0

        # Get completed maintenance costs for the last 6 months.
        six_months_ago = (datetime.now() - timedelta(days=180)).date()
        maintenance_costs = {}
        total_payments = {}

        for prop in properties:
            costs = self.env['real_estate.maintenance_request'].search([
                ('property_id', '=', prop.id),
                ('completion_date', '>=', six_months_ago),
                ('completion_date', '!=', False)
            ])
            maintenance_costs[prop.id] = sum(costs.mapped('actual_cost'))

          
            payments = self.env['lease.payment'].search([
                '|',
                ('property_id', '=', prop.id),
                ('lease_id.property_id', '=', prop.id),
                ('state', 'in', ['paid', 'reconciled']),
            ])
            
            
            total_payments[prop.id] = sum(payments.mapped('amount'))

        return {
            'doc_ids': docids,
            'doc_model': 'real_estate.property',
            'docs': properties,
            'occupancy_rate': occupancy_rate,
            'maintenance_costs': maintenance_costs,
            'total_payments': total_payments,
            'report_date': datetime.now(),
        }
   