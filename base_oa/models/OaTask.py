# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class OaTask(models.Model):
    _name = "oa.task"
    _description = "Task"

    name = fields.Char("Name", readonly=True)
    process_id = fields.Many2one("oa.process", "Process", index=True, readonly=True)
    process_code = fields.Char(related="process_id.code", string="Process Code", store=True, index=True, readonly=True)
    task_content = fields.Char("Content", readonly=True)
    process_line_id = fields.Many2one("oa.task.detail", "Cuttent Step", readonly=True)
    res_model = fields.Char("Model", index=True, readonly=True)
    res_id = fields.Integer("Record ID", index=True, readonly=True)
    reference = fields.Char(string='Reference', compute='_compute_reference', readonly=True, store=False)
    lines = fields.One2many("oa.task.detail", "task_id", "Detail", readonly=True)

    state = fields.Selection([("draft", "Draft"), ("process", "Process"), ("done", "Done"), ("cancel", "Cancel")],
        string="Status", default="draft", readonly=True)

    @api.depends('res_model', 'res_id')
    def _compute_reference(self):
        for task in self:
            task.reference = "%s,%s" % (task.res_model, task.res_id)

    @api.multi
    def get_task_by_code(self, res_model, res_id, process_id):
        task_id = self.env["oa.task"].search([("process_id", "=", process_id),
            ("res_model", "=", res_model),
            ("res_id", "=", res_id)],
            limit=1)
        return task_id

    @api.multi
    def action_do(self):
        self.process_line_id.action_done()
        self.action_state()

    @api.multi
    def action_refuse(self):
        self.process_line_id.action_refuse()
        self.action_state()

    def action_state(self):
        line_id = self.get_next_line()
        val = dict()
        if line_id == True:
            val.update({
                "process_line_id": False,
                "state": "done",
            })
            done_func = self.process_id.done_func
            if done_func:
                self.env["oa.base"]._action_func(self.res_model, self.res_id, done_func)

        elif line_id == False:
            val.update({
                "process_line_id": False,
                "state": "cancel",
            })
            cancel_func = self.process_id.cancel_func
            if cancel_func:
                self.env["oa.base"]._action_func(self.res_model, self.res_id, cancel_func)

        else:
            val.update({
                "process_line_id": line_id.id,
                "state": "process",
            })
        self.write(val)

    @api.multi
    def get_next_line(self):
        """

        :return:
            True 布尔值True 该OA流程已经完成
            False 布尔值False 该OA流程已经取消
            line_id 返回流程步骤
        """
        for line in self.lines:
            if line.state == "refused":
                return False
            elif line.state == "draft":
                return line
        return True

    def action_draft(self):
        self.lines.write({
            "state": "draft",
            "handler_id": False,
            "date": False,
        })
        self.action_state()
