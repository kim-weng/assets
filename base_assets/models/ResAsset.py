# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError


class ResAsset(models.Model):
    _name = "res.asset"
    _description = "Assets"
    _inherit = ["mail.thread"]

    code = fields.Char("Code", required=True, copy=False)
    name = fields.Char("Name", required=True, copy=False,)
    sn = fields.Char("SN", copy=False,)
    product_id = fields.Many2one("product.product", "Product")
    value = fields.Float("In Value", digits=dp.get_precision("Product Price"), copy=False,)
    value_residual = fields.Float("Residual Value", digits=dp.get_precision("Product Price"), copy=False,)
    value_min = fields.Float("Min Value", digits=dp.get_precision("Product Price"))
    company_id = fields.Many2one("res.company", "Company", required=True,
        default=lambda self: self.env["res.company"]._company_default_get("res.asset"))
    currency_id = fields.Many2one("res.currency", "Currency", related="company_id.currency_id", readonly=True)
    supplier_id = fields.Many2one("res.partner", "Supplier", domain=[("supplier", "=", True)])
    manufacturer_id = fields.Many2one("res.partner", "Manufacturer")
    note = fields.Text("Notes", copy=False,)
    category_id = fields.Many2one("asset.category", "Categories", required=True)
    date = fields.Datetime("Date", copy=False, default=fields.Datetime.now)
    state = fields.Selection([("draft", "Draft"), ("open", "Open"), ("close", "Close")], string="Status", readonly=True)
    active = fields.Boolean("Active", default=True, copy=False)
    owner_employee_id = fields.Many2one("hr.employee", "Own Employee")
    owner_department_id = fields.Many2one("hr.department", "Own Department")
    employee_id = fields.Many2one("hr.employee", "Employee")
    department_id = fields.Many2one("hr.department", "Department")
    warehouse_id = fields.Many2one("stock.warehouse", "Warehouse")
    location_id = fields.Many2one("stock.location", "Location")
    depreciation_line_ids = fields.One2many("asset.depreciation.line", "asset_id", string="Depreciation Lines")
    move_line_ids = fields.One2many("asset.move.line", "asset_id", string="Asset Move Lines")
    move_ids = fields.One2many("stock.move", "asset_id", string="Asset Stock Move")

    @api.model
    def create(self, values):
        category_id = values.get("category_id", 0)
        ir_seq_code = "res.asset"
        if category_id:
            category_id = self.env["asset.category"].browse(category_id)
            if category_id and category_id.sequence_line_id and category_id.sequence_line_id.code:
                ir_seq_code = category_id.sequence_line_id.code

        values["code"] = self.env["ir.sequence"].next_by_code(ir_seq_code) or "New"
        return super(ResAsset, self).create(values)

    @api.model
    def default_get(self, fields):
        values = super(ResAsset, self).default_get(fields)
        if "company_id" in values:
            company_id = values.get("company_id")
            company_id = self.env["res.company"].browse(company_id)
        else:
            company_id = self.env["res.company"]._company_default_get("res.asset")
            values["company_id"] = company_id.id

        asset_default = company_id._get_default_asset()
        values.update(asset_default)
        values.update({
            "owner_employee_id": asset_default.get("employee_id", False),
            "owner_department_id": asset_default.get("department_id", False),
        })
        return values

    @api.multi
    def action_open(self):
        for asset in self:
            val = {"state": "open"}
            if asset.company_id:
                company_id = asset.company_id
            else:
                company_id = self.env["res.company"]._company_default_get("res.asset")
                val["company_id"] = company_id.id
            asset_default = company_id._get_default_asset()
            val.update(asset_default)
            if not asset.owner_employee_id:
                val["owner_employee_id"] = asset_default.get("employee_id", False)
            if not asset.owner_department_id:
                val["owner_department_id"] = asset_default.get("department_id", False)
            asset.write(val)
        return True

    @api.multi
    def unlink(self):
        for asset in self:
            if asset.state in ("open", "close"):
                raise UserError(_('You cannot delete a asset that is in %s state.') % (asset.state))
            if asset.depreciation_line_ids.filtered(lambda dl: dl.state in ("confirm", "done")) \
                or asset.move_line_ids.filtered(lambda ml: ml.state in ("confirm", "done", "cancel")) \
                or asset.move_ids:
                raise UserError(_('You cannot delete a asset that contains posted depreciation or openration.'))
        return super(ResAsset, self).unlink()

    @api.multi
    def name_get(self):
        result = []
        for asset in self:
            name = asset.name
            if asset.sn:
                name = name + "-%s" % asset.sn
            if asset.code:
                name = "[%s]" % asset.code + name
                result.append((asset.id, name))
        return result

    @api.multi
    def action_close(self):
        for asset in self:
            val = {"state": "close"}
            val.update({
                "owner_employee_id": False,
                "owner_department_id": False,
                "employee_id": False,
                "department_id": False,
                "warehouse_id": False,
                "location_id": False,
            })
            asset.write(val)
        return True

    def action_create(self, vals):
        asset = self.create(vals)
        if asset.category_id.auto_confirm:
            asset.action_open()
        return asset

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        return super(ResAsset, self). search(args, offset, limit, order, count)

    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
        return super(ResAsset, self)._search(args, offset, limit, order, count, access_rights_uid)