# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.osv import expression
from odoo.addons import decimal_precision as dp


status = [("draft", "Draft"), ("confirm", "Confirm"), ("done", "Done"), ("cancel", "Cancel")]


class AssetInventory(models.Model):
    _name = 'asset.inventory.order'
    _inherit = ["oa.base"]

    _description = 'Assets Inventory Order'


    name = fields.Char("Name", copy=False, readonly=True)
    apply_user_id = fields.Many2one("res.users", "Apply Users", default=lambda self: self._uid,
        readonly=True, states={'draft': [('readonly', False)]})
    date = fields.Datetime("Date", default=fields.Datetime.now,
        readonly=True, states={'draft': [('readonly', False)]})
    date_done = fields.Datetime("Date Done", default=fields.Datetime.now,
        readonly=True)
    owner_employee_id = fields.Many2one("hr.employee", "Own Employee",
        readonly=True, states={'draft': [('readonly', False)]})
    owner_department_id = fields.Many2one("hr.department", "Own Department",
        readonly=True, states={'draft': [('readonly', False)]})
    employee_id = fields.Many2one("hr.employee", "Employee",
        readonly=True, states={'draft': [('readonly', False)]})
    department_id = fields.Many2one("hr.department", "Department",
        readonly=True, states={'draft': [('readonly', False)]})
    location_id = fields.Many2one("stock.location", "Location",
        readonly=True, states={'draft': [('readonly', False)]})
    state = fields.Selection(status, string="Status", readonly=True, default="draft")
    company_id = fields.Many2one("res.company", "Company", required=True,
        default=lambda self: self.env['res.company']._company_default_get('asset.picking.order'),
        readonly=True, states={'draft': [('readonly', False)]})
    inventory_line_ids = fields.One2many("asset.inventory.line", "inventory_id", String="Inventory Lines",
        readonly=True, states={'draft': [('readonly', False)], 'confirm': [('readonly', False)]})
    move_line_ids = fields.One2many("asset.move.line", "inventory_id", String="Move Lines",
        readonly=True)


    @api.model
    def create(self, values):
        values["name"] = self.env["ir.sequence"].next_by_code("asset.inventory.order") or "New"
        return super(AssetInventory, self).create(values)

    # 同一时间同一盘点维度只能有一个在进行中
    @api.constrains('state')
    def check_inventory(self):
        for inventory in self.sudo():
            pass

    @api.multi
    def action_inventory(self):
        owner_employee_id = self.owner_employee_id
        owner_department_id = self.owner_department_id
        employee_id = self.employee_id
        department_id = self.department_id
        location_id = self.location_id
        domain = [("active", "=", "True"), ("state", "=", "open")]
        if not owner_employee_id and not owner_department_id and not employee_id and not department_id and not location_id:
            raise UserError(_("You must Inventory By Some Conditions"))
        if owner_employee_id:
            domain = expression.AND([[('owner_employee_id', '=', owner_employee_id.id)], domain])
        if owner_department_id:
            domain = expression.AND([[('owner_department_id', '=', owner_department_id.id)], domain])
        if employee_id:
            domain = expression.AND([[('employee_id', '=', employee_id.id)], domain])
        if department_id:
            domain = expression.AND([[('department_id', '=', department_id.id)], domain])
        if location_id:
            domain = expression.AND([[('location_id', '=', location_id.id)], domain])
        res_asset_obj = self.env["res.asset"]
        inventory_line_ids = []
        res_asset_ids = res_asset_obj.search(domain)
        for res_asset_id in res_asset_ids:
            inventory_line_ids.append((0, 0,{
                "asset_id": res_asset_id.id,
                "code": res_asset_id.code,
                "name": res_asset_id.name,
                "sn": res_asset_id.sn,
                "category_id": res_asset_id.category_id.id,
                "product_id": res_asset_id.product_id.id,
                "value": res_asset_id.value,
                "value_residual": res_asset_id.value_residual,
                "inventory_result": "draft",
            }))
        self.write({"inventory_line_ids": False})
        self.write({"inventory_line_ids": inventory_line_ids, "state": "confirm"})
        return True

    @api.multi
    def action_done(self):
        inventory_line_ids = self.inventory_line_ids.filtered(lambda ili:ili.inventory_result == "draft")
        if inventory_line_ids:
            raise UserError(_("Please comfirm the inventory line by every lines"))

        move_line_ids = []
        date_done = fields.Datetime.now()
        for inventory_line_id in self.inventory_line_ids:
            # 盘盈 资产挂在盘点的主表字段上
            if inventory_line_id.inventory_result == "profit":
                vals = {
                    "name": inventory_line_id.name,
                    "code": inventory_line_id.code,
                    "sn": inventory_line_id.sn,
                    "product_id": inventory_line_id.product_id.id,
                    "category_id": inventory_line_id.asset_category_id.id,
                    "value": self.value,
                    "value_residual": self.value,
                    "company_id": self.order_id.company_id.id,
                    "currency_id": self.order_id.currency_id.id,
                    "date": date_done,
                    "state": "draft",
                }
                asset = self.env["res.asset"].action_create(vals)
                move_line_ids.append({
                    "name": "Inventory %s"%(inventory_line_id.asset_id.display_name),
                    "inventory_id": self.id,
                    "asset_id": asset.id,
                    "product_id": asset.product_id.id,
                    "date": self.date_done,
                    "dest_owner_employee_id": self.owner_employee_id,
                    "dest_owner_department_id": self.owner_department_id,
                    "dest_employee_id": self.employee_id,
                    "dest_department_id": self.department_id,
                    "dest_location_id": self.location_id,
                    "state": "done",
                })
            # 盘亏 资产关闭 字段置空
            elif inventory_line_id.inventory_result == "loss":
                move_line_ids.append({
                    "name": "Inventory %s" % (inventory_line_id.asset_id.display_name),
                    "inventory_id": self.id,
                    "asset_id": inventory_line_id.asset_id.id,
                    "product_id": inventory_line_id.asset_id.product_id.id,
                    "date": self.date_done,
                    "dest_owner_employee_id": False,
                    "dest_owner_department_id": False,
                    "dest_employee_id": False,
                    "dest_department_id": False,
                    "dest_location_id": False,
                    "state": "done",
                })
            # 确认 资产无发生变化
            elif inventory_line_id.inventory_result == "comfirm":
                pass
            else:
                raise UserError(_("Error Inventory Result"))
        val = {"state": "done"}
        if move_line_ids:
            val["move_line_ids"] = move_line_ids
        self.write(val)
        return True

    @api.multi
    def action_cancel(self):
        self.write({"state": "cancel"})
        self.inventory_line_ids.write({"state": "cancel"})
        self.move_line_ids.action_cancel()

class AssetInventoryLine(models.Model):
    _name = "asset.inventory.line"

    inventory_id = fields.Many2one("asset.inventory.order", "Inventory")
    asset_id = fields.Many2one("res.asset", "Asset", readonly=True)
    category_id = fields.Many2one("asset.category", "Categories", required=True, copy=False)
    product_id = fields.Many2one("product.product", "Product")
    code = fields.Char("Code", required=True, copy=False,)
    name = fields.Char("Name", required=True, copy=False,)
    sn = fields.Char("SN", copy=False)
    inventory_result = fields.Selection([("draft", "Draft"), ("profit", "Profit"), ("loss", "Loss"), ("comfirm", "Comfirm")],
        string="Inventory Result", default="profit", required=True)
    value = fields.Float("In Value", digits=dp.get_precision("Product Price"), copy=False,)
    value_residual = fields.Float("Residual Value", digits=dp.get_precision("Product Price"), copy=False,)
    state = fields.Selection(status, string="Status", readonly=True, releted="asset_id.asset_id",
        store=True)
    company_id = fields.Many2one("res.company", "Company", releted="asset_id.company_id",
        readonly=True, states={'draft': [('readonly', False)]})

    @api.constrains('asset_id', 'inventory_result')
    def check_line(self):
        for line in self.sudo():
            if line.asset_id:
                if self.inventory_result == "profit":
                    raise UserError(_("The Asset already exists and can not profit"))
            else:
                if self.inventory_result == "comfirm":
                    raise UserError(_("The Asset don't exist and cannot be confirmed"))
