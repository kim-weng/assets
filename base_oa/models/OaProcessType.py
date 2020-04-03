# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class OaProcessType(models.Model):
    _name = 'oa.process.type'
    _description = "Process Type"

    name = fields.Char("Name")
    code = fields.Char("Code")