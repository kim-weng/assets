# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.osv import expression


class OaProcess(models.Model):
    _name = "oa.process"
    _description = "Process"

    name = fields.Char("Name")
    code = fields.Char("Code")
    oa_process_type = fields.Many2one("oa.process.type", "Process Type")
    description = fields.Char("Description")
    model = fields.Char("Model")
    done_func = fields.Char("Func By Done")
    cancel_func = fields.Char("Func By Cancel")
    step_ids = fields.One2many("oa.process.step", "process_id", "Steps")

    _sql_constraints = [
        ("code_uniq", "unique(code)", "The code of the OA-Process must be unique!"),
    ]

    def get_process_by_code(self, model, code=False):
        domain = [("model", "=", model)]
        if code:
            domain = expression.AND(domain, [("code", "=", code)])
        process_id = self.env["oa.process"].search(domain, limit=1)
        if not process_id:
            model = self.env[model]
            raise UserError(_("The %s can't find the process named %s"%(model._description, code)))
        return process_id
