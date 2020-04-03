# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class StockMove(models.Model):
    _inherit = 'stock.move'

    asset_id = fields.Many2one("res.asset", "Asset")
    asset_picking_order_id = fields.Many2one("asset.picking.order", "Asset Picking order")