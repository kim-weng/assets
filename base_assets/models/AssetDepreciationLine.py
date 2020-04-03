# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class AssetDepreciationLine(models.Model):
    _name = 'asset.depreciation.line'

    name = fields.Char("Name")
    asset_id = fields.Many2one("res.asset", "Asset")
    amount_before = fields.Float("Amount Before")
    amount = fields.Float("Amount")
    amount_after = fields.Float("Amount After")
    date = fields.Datetime("Date")
    account_move_id = fields.Many2one("account.move", "Account Move")
    state = fields.Selection([("draft", "Draft"), ("confirm", "Confirm"), ("done", "Done")],
        string="Status", readonly=True, required=True, default=True)