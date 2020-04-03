# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class ResUsers(models.Model):
    _inherit = 'res.users'

    employee_id = fields.Many2one("hr.employee", "Employee", compute="_get_employee", inverse="_set_employee")
    department_id = fields.Many2one("hr.department", "Department", compute="_get_employee", inverse="_set_employee")

    @api.multi
    @api.depends("employee_ids")
    def _get_employee(self):
        for user in self:
            if user.employee_ids:
                user.employee_id = user.employee_ids[0].id
                user.department_id = user.employee_ids[0].department_id.id
            else:
                user.employee_id = False
                user.department_id = False

    @api.one
    def _set_employee(self):
        pass