# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError


status = [("draft", "Draft"), ("confirm", "Confirm"), ("done", "Done"), ("cancel", "Cancel")]


class AssetPickingOrder(models.Model):
    _name = 'asset.picking.order'
    _inherit = ["oa.base"]

    _description = 'Assets Picking Order'


    name = fields.Char("Name", copy=False, readonly=True)
    apply_user_id = fields.Many2one("res.users", "Apply Users", default=lambda self: self._uid,
        readonly=True, states={'draft': [('readonly', False)]})
    apply_employee_id = fields.Many2one("hr.employee", "Apply Employee",
        readonly=True, states={'draft': [('readonly', False)]})
    apply_department_id = fields.Many2one("hr.department", "Apply Department",
        readonly=True, states={'draft': [('readonly', False)]})
    date = fields.Datetime("Date", default=fields.Datetime.now,
        readonly=True, states={'draft': [('readonly', False)]})
    type = fields.Selection([("own", "Own"), ("transfer", "Transfer"), ("fix", "Fix"), ("stock", "Stock")],
        string="Picking Type", default="transfer",
        readonly=True, states={'draft': [('readonly', False)]})
    owner_employee_id = fields.Many2one("hr.employee", "Own Employee",
        readonly=True, states={'draft': [('readonly', False)]})
    dest_owner_employee_id = fields.Many2one("hr.employee", "Dest Own Employee",
        readonly=True, states={'draft': [('readonly', False)]})
    owner_department_id = fields.Many2one("hr.department", "Own Department",
        readonly=True, states={'draft': [('readonly', False)]})
    dest_owner_department_id = fields.Many2one("hr.department", "Dest Own Department",
        readonly=True, states={'draft': [('readonly', False)]})
    employee_id = fields.Many2one("hr.employee", "Employee",
        readonly=True, states={'draft': [('readonly', False)]})
    dest_employee_id = fields.Many2one("hr.employee", "Dest Employee",
        readonly=True, states={'draft': [('readonly', False)]})
    department_id = fields.Many2one("hr.department", "Department",
        readonly=True, states={'draft': [('readonly', False)]})
    dest_department_id = fields.Many2one("hr.department", "Dest Department",
        readonly=True, states={'draft': [('readonly', False)]})
    warehouse_id = fields.Many2one("stock.warehouse", "Warehouse",
        readonly=True, states={'draft': [('readonly', False)]})
    dest_warehouse_id = fields.Many2one("stock.warehouse", "Dest Warehouse",
        readonly=True, states={'draft': [('readonly', False)]})
    location_id = fields.Many2one("stock.location", "Location",
        readonly=True, states={'draft': [('readonly', False)]})
    dest_location_id = fields.Many2one("stock.location", "Dest Location",
        readonly=True, states={'draft': [('readonly', False)]})
    state = fields.Selection(status, string="Status", readonly=True, default="draft")
    company_id = fields.Many2one("res.company", "Company", required=True,
        default=lambda self: self.env['res.company']._company_default_get('asset.picking.order'),
        readonly=True, states={'draft': [('readonly', False)]})
    line_ids = fields.One2many("asset.move.line", "order_id", String="Lines",
        readonly=True, states={'draft': [('readonly', False)], 'confirm': [('readonly', False)]})
    picking_ids = fields.Many2many("stock.picking", "asset_order_picking_rel",
        "order_id", "picking_id", String="Stock Picking", readonly=True, copy=False)
    picking_count = fields.Integer("Picking Count", compute="_get_picking_count", store=True)
    stock_move_ids = fields.One2many("stock.move", "asset_picking_order_id", String="Stock Moves", readonly=True)

    @api.onchange("apply_user_id")
    def _onchange_apply_user_id(self):
        self.apply_employee_id = self.apply_user_id.employee_id.id
        self.apply_department_id = self.apply_user_id.department_id.id


    @api.model
    def create(self, values):
        values["name"] = self.env["ir.sequence"].next_by_code("asset.picking.order") or "New"
        return super(AssetPickingOrder, self).create(values)

    @api.depends("picking_ids")
    def _get_picking_count(self):
        for picking in self:
            picking.picking_count = len(picking.picking_ids)

    # 确认资产转移单
    # 检查是否生成拣货单(stock.picking)
    @api.multi
    def action_comfirm(self):
        self.ensure_one()
        vals = {"state": "confirm"}

        if not self.picking_ids and self.location_id.id != self.dest_location_id.id:
            move_lines = []
            for line in self.line_ids:
                move_lines.append((0, 0, {
                    "name": line.product_id.display_name,
                    "product_id": line.product_id.id,
                    "product_uom": line.product_id.uom_id.id,
                    "product_uom_qty": 1,
                    "asset_id": line.asset_id.id,
                    "location_id": line.location_id.id or self.location_id.id,
                    "dest_location_id": line.dest_location_id.id or self.dest_location_id.id,
                }))
            picking = self.env["stock.picking"].create({
                "location_id": self.location_id.id,
                "location_dest_id": self.dest_location_id.id,
                "picking_type_id": self.env.ref("stock.picking_type_internal").id,
                "move_lines": move_lines,
                "origin": self.name,
            })
            vals["picking_ids"] = [(4, picking.id)]

        self.write(vals)
        self.line_ids.action_confirm()
        return True

    # 完成资产转移单
    # 检查涉及的拣货单(stock.picking),未完成则提示
    # 若所有的拣货单均已取消，则整张单取消
    # 完成时,重写资产上的部门,员工,仓库,库位信息
    @api.multi
    def action_done(self):
        self.ensure_one()
        val = {}
        if any(picking.state not in ("done", "cancel") for picking in self.picking_ids):
            raise UserError(_("You still have some stock picking to finish!"))

        if all(picking.state == "cancel" for picking in self.picking_ids):
            val["state"] = "cancel"
            self.line_ids.write({"state": "cancel"})
        else:
            val["state"] = "done"
        self.write(val)

        self.line_ids.filtered(lambda l:l.state == "confirm").action_done()
        return True

    @api.multi
    def action_cancel(self):
        self.line_ids.action_cancel()
        self.write({"state": "cancel"})

    # 查看相应的拣货单
    @api.multi
    def action_view_picking(self):
        action = self.env.ref('stock.action_picking_tree_all')
        result = action.read()[0]

        result['context'] = {}
        pick_ids = self.mapped('picking_ids')
        form = self.env.ref('base_assets.view_picking_form_inherit_assets', False)
        result['views'] = [(form and form.id or False, 'form'), (False, 'tree'), (False, 'kanban'), (False, 'calendar')]

        if not pick_ids or len(pick_ids) > 1:
            result['domain'] = "[('id','in',%s)]" % (pick_ids.ids)
        elif len(pick_ids) == 1:
            result['res_id'] = pick_ids.id
        return result