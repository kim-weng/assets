# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.tools.float_utils import float_round
from odoo.osv import expression


order_type_selection = [("normal", "Normal"), ("asset", "Asset")]


class PurchaseOrder(models.Model):
    _name = "purchase.order"
    _inherit = ["purchase.order", "oa.base"]

    order_type = fields.Selection(order_type_selection, string="Normal/Asset",
        default="normal", required=True)

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        context = self._context
        if "active_test" not in context:
            # 默认不选择资产类产品
            # context包含select_asset:选择资产类采购订单
            # context包含select_all:选择所有采购订单
            # 其余情况：只查看普通采购订单
            if not context.get("select_asset", False):
                args = expression.AND([args, [("order_type", "=", "normal")]])
            elif context.get("select_all", False):
                pass
            else:
                args = expression.AND([args, [("order_type", "=", "asset")]])
        return super(PurchaseOrder, self).search(args, offset, limit, order, count)

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        if view_type == "form" and self._context.get("select_asset", False):
            view_id = self.env.ref("base_assets.purchase_order_form_inherit_assets").id
        return super(PurchaseOrder, self).fields_view_get(view_id, view_type, toolbar, submenu)

    @api.multi
    def button_confirm(self):
        for order in self:
            # 资产的采购数量必须是整型，取整，拆解明细行
            for line in order.order_line.filtered(lambda ol:
                ol.product_id.is_asset and ol.product_id.asset_category_id):
                product_qty = float_round(line.product_uom_qty, precision_rounding=1, rounding_method="DOWN")
                line.write({"product_qty": 1})
                while(product_qty > 1):
                    line = line.copy({"product_qty": 1})
                    product_qty -= 1

            order.order_line.filtered(lambda ol:
                ol.product_id.is_asset and ol.product_id.asset_category_id).asset_create()
        res = super(PurchaseOrder, self).button_confirm()

        # 创建资产调拨单
        for purchase_order in self.filtered(lambda s: s.order_type == "asset"):
            asset_picking_order = self.env["asset.picking.order"].create(purchase_order._create_asset_picking_order_val())
            move_ids = purchase_order.mapped("picking_ids").mapped("move_lines")
            if move_ids:
                move_ids.write({"asset_picking_order_id": asset_picking_order.id})
            asset_picking_order.action_comfirm()

        return res

    def _create_asset_picking_order_val(self):
        self.ensure_one()
        if self.picking_type_id.default_location_src_id:
            location_id = self.picking_type_id.default_location_src_id.id
        elif self.partner_id:
            location_id = self.partner_id.property_stock_supplier.id
        else:
            customerloc, location_id = self.env['stock.warehouse']._get_partner_locations()
        location_dest_id = self.picking_type_id.default_location_dest_id.id
        vals = {
            "type": "stock",
            "location_id": location_id,
            "dest_location_id": location_dest_id,
        }

        line_ids = []
        for line in self.order_line:
            line_ids.append((0, 0, line._create_asset_move_line_val(location_id, location_dest_id)))
        if line_ids:
            vals["line_ids"] = line_ids

        picking_ids = self.picking_ids.ids
        if picking_ids:
            vals["picking_ids"] = [(6, 0, picking_ids)]
        return vals

    def test_done(self):
        print ("done")

    def test_cancel(self):
        print ("cancel")

class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    asset_id = fields.Many2one("res.asset", "Asset", copy=False)
    order_type = fields.Selection(order_type_selection, "Purchase Order Type", relation="order_id.order_type",
        store=True)

    @api.one
    def asset_create(self):
        product_id = self.product_id
        asset_category_id = product_id.asset_category_id
        if asset_category_id:
            vals = {
                "name": product_id.name,
                "product_id": product_id.id,
                "category_id": asset_category_id.id,
                "value": self.price_subtotal,
                "supplier_id": self.order_id.partner_id.id,
                "company_id": self.order_id.company_id.id,
                "currency_id": self.order_id.currency_id.id,
                "date": self.order_id.date_order,
                "warehouse_id": self.order_id.picking_type_id.warehouse_id.id,
                "location_id": self.order_id.picking_type_id.default_location_dest_id.id,
                "state": "draft",
            }

            asset = self.env["res.asset"].action_create(vals)
            self.write({"asset_id": asset.id})
        return True

    @api.multi
    def _prepare_stock_moves(self, picking):
        res = super(PurchaseOrderLine, self)._prepare_stock_moves(picking)
        asset_id = self.asset_id.id or False
        if asset_id:
            for r in res:
                r["asset_id"] = asset_id
        return res

    def _create_asset_move_line_val(self, location_id, dest_location_id):
        self.ensure_one()
        vals = {
            "name": self.product_id.display_name,
            "asset_id": self.asset_id.id,
            "product_id": self.product_id.id,
            "location_id": location_id,
            "dest_location_id": dest_location_id,
        }
        return vals