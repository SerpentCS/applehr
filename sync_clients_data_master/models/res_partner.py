from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    def _compute_agent_bills_count(self):
        for rec in self:
            rec.agent_bills_count = rec.env["account.move"].search_count(
                [
                    ("partner_id", "=", self.id),
                    ("move_type", "in", ("in_invoice", "in_refund")),
                ]
            )

    remote_servers_ids = fields.One2many("remote.server", "partner_id", "Remote Server")
    agent_id = fields.Many2one("res.partner", string="Agent")
    agent_commission = fields.Float(string="Commission")
    is_agent = fields.Boolean()
    pan_number = fields.Char()
    agent_bills_count = fields.Integer(
        compute="_compute_agent_bills_count", string="Agent Bills"
    )
    balance = fields.Float(string="Balance")
    one_time_charge = fields.Float(string="One Time Charge")
    days_one_time_charge = fields.Integer(string="Days (One Time Charge)")
    minimum_balance = fields.Float(string="Minimum Balance")

    def action_customer_balance_history(self):
        view_id = self.env.ref(
            'sync_clients_data_master.balance_history_tree_views')
        return {
            'name': 'Balance History',
            'type': 'ir.actions.act_window',
            'view_id': view_id.id,
            'view_type': 'form',
            'view_mode': 'tree',
            'res_model': 'balance.history',
            'domain': [('partner_id', '=', self.id)],
            'context': {'create': False, 'delete': False, 'edit': False}
        }
