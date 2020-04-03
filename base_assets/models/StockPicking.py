# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class StockPicking(models.Model):
    _inherit = "stock.picking"

    asset_picking_order_ids = fields.Many2many("asset.picking.order", "asset_order_picking_rel",
        "picking_id", "order_id", String="Asset Picking")
