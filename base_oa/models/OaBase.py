# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class OaBase(models.AbstractModel):
    _name = 'oa.base'

    def _get_oa_state(self):
        state = [("oa_unstart", "OA Unstart")]
        try:
            process_id = self.env["oa.process"].get_process_by_code(self._name)
            step_ids = process_id.step_ids
            state.extend([(step.code, step.name) for step in step_ids])
        except UserError as e:
            pass
        state.append(("oa_cancel", "Cancel"))
        return state

    task_ids = fields.Many2many("oa.task", compute="_get_task", string="OA Tasks", copy=False)
    oa_state = fields.Selection(_get_oa_state, string="OA Status", default="oa_unstart", required=True, copy=False)


    @api.depends()
    def _get_task(self):
        oa_task_obj = self.env["oa.task"]
        for base in self:
            base.task_ids = oa_task_obj.search([("res_model", "=", base._name), ("res_id", "=", base.id)])

    # 确定/拒绝当前OA流程
    @api.multi
    def next_oa(self, context=None, oa_code=False):
        if not oa_code:
            oa_code = context.get("oa_code", False)
        oa_action = context.get("oa_action", False)

        oa_process_env = self.env["oa.process"]
        oa_task_env = self.env["oa.task"]

        res_model = self._name
        for record in self:
            res_id = record.id

            process_id = oa_process_env.get_process_by_code(res_model, oa_code)
            task_id = oa_task_env.get_task_by_code(res_model, res_id, process_id.id)
            if not task_id:
                task_id = self.start_oa(process_id)

            task_id.action_do()
        return self.action_view_oa()

    # 创建新的oa流程
    def start_oa(self, process_id, res_model=False, res_id=False):
        oa_task_env = self.env["oa.task"]

        if not res_model:
            res_model = self._name
        if not res_id:
            res_id = self.id

        record = self.env[res_model].browse(res_id)
        task_val = {
            "name": _("%s %s") % (record.display_name, process_id.name),
            "process_id": process_id.id,
            "process_code": process_id.code,
            "task_content": process_id.description,
            "res_model": res_model,
            "res_id": res_id,
        }
        step_ids = []
        for step in process_id.step_ids:
            task_step = 1
            step_ids.append((0, 0, {
                "process_step_id": step.id,
                "task_step": task_step,
                "name": step.name,
                "handle_content": step.description,
            }))
        if step_ids:
            task_val["lines"] = step_ids
        task_id = oa_task_env.create(task_val)
        return task_id

    # 查看此单据的oa流程
    @api.multi
    def action_view_oa(self):
        oa_task_action = self.env.ref("base_oa.oa_task_action").read()[0]
        task_ids = self.task_ids
        if len(task_ids) == 1:
            oa_task_action['views'] = [(self.env.ref('base_oa.oa_task_form_view').id, 'form')]
            oa_task_action["res_id"] = task_ids.id
        elif len(task_ids) > 1:
            oa_task_action["domain"] = [('id', 'in', task_ids.ids)]
        else:
            raise UserError(_("OA Process has not been started!"))
        return oa_task_action

    # 尝试执行某个方法
    def _action_func(self, res_model, res_id, func):
        if not res_model:
            res_model = self._name
        if not res_id:
            res_id = self.id

        env = self.env[res_model]
        if hasattr(env, func):
            record = env.browse(res_id)
            getattr(record, func)()