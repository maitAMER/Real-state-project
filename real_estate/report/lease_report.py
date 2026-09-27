# -*- coding: utf-8 -*-
from odoo import api, models
class LeaseReportSummary(models.AbstractModel):
    _name = 'report.real_estate.report_lease_summary'
    _description = 'Lease Summary Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        leases = self.env['real_estate.lease'].browse(docids).exists()
        
        maintenance_request_history = {}
        total_actual_costs = {}

        for lease in leases:
            requests = lease.maintenance_request_ids.sorted(
                key=lambda request: (request.create_date or request.write_date, request.id)
            )
            maintenance_request_history[lease.id] = requests
            total_actual_costs[lease.id] = sum(requests.mapped('actual_cost'))

        return {
            'doc_ids': leases.ids,
            'doc_model': 'real_estate.lease',
            'docs': leases,
            'maintenance_request_history': maintenance_request_history,
            'total_actual_costs': total_actual_costs,    
        }