# -*- encoding: utf-8 -*-
from odoo import fields, models


class DecontaminationConfirm(models.TransientModel):
    _name = 'decontamination.confirm'
    _description = 'Decontamination Confirm'

    decontamination_id = fields.Many2one('decontamination.report', string='Decontamination')

    def action_proceed(self):
        for confirm_obj in self:
            confirm_obj.decontamination_id.action_confirm()
        return {'type': 'ir.actions.act_window_close'}
