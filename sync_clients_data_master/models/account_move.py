# -*- coding: utf-8 -*-

from odoo import fields, models


class AccountMove(models.Model):
    _inherit = 'account.move'

    move_type = fields.Selection(selection_add=[('in_invoice', 'Bill')])


class AccountMove(models.Model):
    _inherit = 'account.move.line'

    remote_server_id = fields.Many2one('remote.server', string='Service')
