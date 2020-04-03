# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.osv import expression


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    is_asset = fields.Boolean("Is Asset")
    asset_category_id = fields.Many2one("asset.category", "Asset Category")

    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
        context = self._context
        # 默认不选择资产类产品
        # context包含select_asset:选择资产类产品,
        if not context.get("select_asset", False):
            args = expression.AND([args, [("is_asset", "=", False)]])
        else:
            args = expression.AND([args, [("is_asset", "=", True)]])
        return super(ProductTemplate, self)._search(args, offset, limit, order, count, access_rights_uid)

class ProductProduct(models.Model):
    _inherit = 'product.product'


    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
        context = self._context
        # 默认不选择资产类产品
        # context包含select_asset:选择资产类产品,
        if not context.get("select_asset", False):
            args = expression.AND([args, [("is_asset", "=", False)]])
        else:
            args = expression.AND([args, [("is_asset", "=", True)]])
        return super(ProductProduct, self)._search(args, offset, limit, order, count, access_rights_uid)
