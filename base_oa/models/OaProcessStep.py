# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class OaProcess(models.Model):
    _name = 'oa.process.step'
    _description = "Process Step"
    _order = "seq, id"

    process_id = fields.Many2one("oa.process", "Process")
    seq = fields.Integer("Seq")
    name = fields.Char("Name")
    code = fields.Char("Code")
    group_id = fields.Many2one("res.groups", "Goups")
    done_func = fields.Char("Func By Done")
    cancel_func = fields.Char("Func By Cancel")
    description = fields.Char("Description")
