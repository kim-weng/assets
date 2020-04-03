# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class AssetCategory(models.Model):
    _name = 'asset.category'
    _description = 'Asset Category'
    _inherit = ['mail.thread']
    _rec_name = 'complete_name'
    _order = 'complete_name'


    code = fields.Char("Code", required=True)
    name = fields.Char("Name", required=True)
    complete_name = fields.Char('Complete Name', compute='_compute_complete_name', store=True)
    parent_id = fields.Many2one("asset.category", "Parent", index=True)
    asset_account_id = fields.Many2one("account.account", "Asset Account", company_dependent=True,)
    asset_depreciation_account_id = fields.Many2one("account.account", "Asset Depreciation Account", company_dependent=True)
    asset_expense_account_id = fields.Many2one("account.account", "Asset Expend Account", company_dependent=True)
    journal_id = fields.Many2one("account.journal", "Journal", company_dependent=True)
    company_id = fields.Many2one("res.company", "Company", required=True,
        default=lambda self: self.env['res.company']._company_default_get('asset.category'))
    auto_confirm = fields.Boolean(string='Auto-Confirm Assets', default=False)
    sequence_line_id = fields.Many2one('ir.sequence', string='Code of Assets Sequence', readonly=True, copy=False)
    active = fields.Boolean("Active", default=True, copy=False)

    _sql_constraints = [('uniq_code', 'unique(code)', "The code of the Assets must be unique !")]

    @api.depends('name', 'code', 'parent_id.complete_name')
    def _compute_complete_name(self):
        for asset in self:
            name = "[%s]%s" % (asset.code, asset.name)
            if asset.parent_id:
                asset.complete_name = '%s / %s' % (asset.parent_id.complete_name, name)
            else:
                asset.complete_name = name
