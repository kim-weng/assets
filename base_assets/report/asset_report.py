# -*- coding: utf-8 -*-
from odoo import tools
from odoo import api, fields, models
from odoo.addons import decimal_precision as dp


class AssetsReport(models.Model):
    _name = "assets.report"
    _description = "Assets Report"
    _auto = False
    _rec_name = 'asset_id'
    _order = 'asset_id desc'

    asset_id = fields.Many2one("res.asset", "Asset")
    category_id = fields.Many2one("asset.category", "Categories")
    date = fields.Datetime("Date", copy=False, default=fields.Datetime.now)
    product_id = fields.Many2one("product.product", "Product")
    owner_employee_id = fields.Many2one("hr.employee", "Own Employee")
    owner_department_id = fields.Many2one("hr.department", "Own Department")
    employee_id = fields.Many2one("hr.employee", "Employee")
    department_id = fields.Many2one("hr.department", "Department")
    location_id = fields.Many2one("stock.location", "Location")
    value = fields.Float("In Value", digits=dp.get_precision("Product Price"), copy=False,)

    #
    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""CREATE or REPLACE VIEW %s as (%s)""" % (self._table, self._query(
            fields=self._get_fields(),
            from_clause=self._from_clause(),
            where_=self._where_()
        )))

    def _query(self, with_clause='', fields={}, groupby='', from_clause="", where_="", orderby_=""):
        with_ = ("WITH %s" % with_clause) if with_clause else ""

        select_ = """
        """

        for field in fields.values():
            select_ += field

        from_ = """ %s
        """ % from_clause

        if groupby:
            groupby_ = """ GROUP BY %s
            """ % (groupby)
        else:
            groupby_ = ""

        return '%s SELECT %s ' \
               ' FROM %s ' \
               ' WHERE 1=1 %s ' \
               ' %s ' % (with_, select_, from_, where_, groupby_)

    def _get_fields(self):
        return {
            "margin": """ ra.id as id, 
            ra.id as asset_id,
            ra.category_id as category_id,
            ra.date as date,
            ra.product_id as product_id,
            ra.owner_employee_id as owner_employee_id,
            ra.owner_department_id as owner_department_id,
            ra.employee_id as employee_id,
            ra.department_id as department_id,
            ra.location_id as location_id,
            ra.value as value """
        }

    def _from_clause(self):
        return " res_asset ra "

    def _where_(self):
        return " and state = 'open' "
