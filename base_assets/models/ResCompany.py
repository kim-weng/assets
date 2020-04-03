# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class ResCompany(models.Model):
    _inherit = 'res.company'

    default_asset_employee_id = fields.Many2one("hr.employee", "Default Employee of Assets")
    default_asset_department_id = fields.Many2one("hr.department", "Default Department of Assets")
    default_asset_warehouse_id = fields.Many2one("stock.warehouse", "Default Employee of Warehouse")
    default_asset_location_id = fields.Many2one("stock.location", "Default Employee of Location")

    def _get_default_asset(self):
        return {
            "employee_id": self.default_asset_employee_id.id,
            "department_id": self.default_asset_department_id.id,
            "warehouse_id": self.default_asset_warehouse_id.id,
            "location_id": self.default_asset_location_id.id,
        }