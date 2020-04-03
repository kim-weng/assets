# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, AccessError


class OaTaskDetail(models.Model):
    _name = "oa.task.detail"
    _description = "Task Detail"
    _order = "task_id, task_step"

    task_id = fields.Many2one("oa.task", "Process")
    res_model = fields.Char("Model", related="task_id.res_model", store=True, index=True)
    res_id = fields.Integer("Record ID", related="task_id.res_id", store=True, index=True)
    task_step = fields.Integer("Step")
    process_step_id = fields.Many2one("oa.process.step", "Step", index=True, readonly=True)
    name = fields.Char("Name")
    handle_content = fields.Char("Handle Content")
    handler_id = fields.Many2one("res.users", "Hanlder Users")
    date = fields.Datetime("Hanlder Datetime")
    state = fields.Selection([("draft", "Draft"), ("done", "Done"), ("refused", "Refused")],
        string="draft", default="draft", readonly=True, required=True)

    @api.multi
    def action_done(self):
        self._action_state("done")
        done_func = self.process_step_id.done_func
        if done_func:
            self.env["oa.base"]._action_func(self.res_model, self.res_id, done_func)

    @api.multi
    def action_refuse(self):
        self._action_state("refused")
        cancel_func = self.process_step_id.cancel_func
        if cancel_func:
            self.env["oa.base"]._action_func(self.res_model, self.res_id, cancel_func)

    @api.multi
    def _action_state(self, state="done"):
        if len(self) > 1:
            raise UserError(_("Please Deal One Record!"))
        elif len(self) == 0:
            return False

        # 检测权限组
        group_id = self.process_step_id.group_id
        if group_id and group_id not in self.env.user.groups_id:
            raise AccessError(_("Do not have access to the oa task!%s Can!")%(group_id.display_name))

        if self.state == "done":
            raise UserError(_("The OA Step called %s is done!" % (self.name)))
        elif self.state == "refuse":
            raise UserError(_("The OA Step called %s is refused!" % (self.name)))
        val = {
            "handler_id": self._uid,
            "date": fields.datetime.now(),
            "state": state,
        }
        self.write(val)
        return True