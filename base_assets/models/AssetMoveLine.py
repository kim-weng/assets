# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.osv import expression
from odoo.addons import decimal_precision as dp
from . import AssetPicking


status = AssetPicking.status


class AssetMoveLine(models.Model):
    _name = "asset.move.line"
    _description = "Assets Move Line"

    name = fields.Char("Name")
    order_id = fields.Many2one("asset.picking.order", "Order")
    inventory_id = fields.Many2one("asset.inventory.order", "Inventory")
    asset_id = fields.Many2one("res.asset", "Asset", required=True,
        # domain="["
        #        "'|', ('owner_employee_id', '=', owner_employee_id), ('owner_employee_id', '=', False),"
        #        "'|', ('owner_department_id', '=', owner_department_id), ('owner_department_id', '=', False),"
        #        "'|', ('employee_id', '=', employee_id), ('employee_id', '=', False),"
        #        "'|', ('department_id', '=', department_id), ('department_id', '=', False),"
        #        "'|', ('warehouse_id', '=', warehouse_id), ('warehouse_id', '=', False),"
        #        "'|', ('location_id', '=', location_id), ('location_id', '=', False)"
        #        "]"
                               )
    product_id = fields.Many2one("product.product", "Product", required=True)
    date = fields.Datetime("Date", copy=False, readonly=True)
    owner_employee_id = fields.Many2one("hr.employee", "Own Employee")
    dest_owner_employee_id = fields.Many2one("hr.employee", "Dest Own Employee")
    owner_department_id = fields.Many2one("hr.department", "Own Department")
    dest_owner_department_id = fields.Many2one("hr.department", "Dest Own Department")
    employee_id = fields.Many2one("hr.employee", "Employee")
    dest_employee_id = fields.Many2one("hr.employee", "Dest Employee")
    department_id = fields.Many2one("hr.department", "Department")
    dest_department_id = fields.Many2one("hr.department", "Dest Department")
    warehouse_id = fields.Many2one("stock.warehouse", "Warehouse")
    dest_warehouse_id = fields.Many2one("stock.warehouse", "Dest Warehouse")
    location_id = fields.Many2one("stock.location", "Location")
    dest_location_id = fields.Many2one("stock.location", "Dest Location")
    state = fields.Selection(status, string="Status", store=True)
    note = fields.Char("Note")
    company_id = fields.Many2one("res.company", "Company", required=True,
        default=lambda self: self.env['res.company']._company_default_get('asset.move.line'))

    _sql_constraints = [
        ('line_uniq_byorder', 'unique(order_id, asset_id)', 'Asset should be unique in a order!'),
        ('line_uniq_byinventory', 'unique(inventory_id, asset_id)', 'Asset should be unique in a inventory!')
    ]

    # 源信息改变 明细行的资产跟着改变
    @api.onchange("asset_id")
    def onchange_asset_id(self):
        self.product_id = self.asset_id.product_id.id
        self.owner_employee_id = self.asset_id.owner_employee_id.id
        self.owner_department_id = self.asset_id.owner_department_id.id
        self.employee_id = self.asset_id.employee_id.id
        self.department_id = self.asset_id.department_id.id
        self.warehouse_id = self.asset_id.warehouse_id.id
        self.location_id = self.asset_id.location_id.id


    @api.multi
    def action_cancel(self):
        self.write({"state": "cancel"})

    @api.multi
    def action_confirm(self):
        self.write({"state": "confirm"})

    @api.multi
    def action_done(self):
        for line in self:
            val = {}
            if line.owner_employee_id and line.dest_owner_employee_id \
                    and line.owner_employee_id != line.dest_owner_employee_id:
                val["owner_employee_id"] = line.dest_owner_employee_id.id

            if line.owner_department_id and line.dest_owner_department_id \
                    and line.owner_department_id != line.dest_owner_department_id:
                val["owner_department_id"] = line.dest_owner_department_id.id

            if line.employee_id and line.dest_employee_id \
                    and line.employee_id != line.dest_employee_id:
                val["employee_id"] = line.dest_employee_id.id

            if line.department_id and line.dest_department_id \
                    and line.department_id != line.dest_department_id:
                val["department_id"] = line.dest_department_id.id

            if line.warehouse_id and line.dest_warehouse_id \
                    and line.warehouse_id != line.dest_warehouse_id:
                val["warehouse_id"] = line.dest_warehouse_id.id

            if line.location_id and line.dest_location_id \
                    and line.location_id != line.dest_location_id:
                val["location_id"] = line.dest_location_id.id

            if val:
                line.asset_id.write(val)
            line.write({"state": "done"})
        line_open = self.filtered(lambda l:
            (l.owner_employee_id or l.owner_department_id or l.employee_id or l.department_id or l.location_id)
            and l.asset_id.state != 'open'
        )
        if line_open:
            line_open.mapped("asset_id").action_open()
        line_close = self.filtered(lambda l:
            not l.owner_employee_id and not l.owner_department_id and not l.employee_id \
            and not l.department_id and not l.location_id \
            and l.asset_id.state != 'close'
        )
        if line_close:
            line_close.mapped("asset_id").action_close()
        return True