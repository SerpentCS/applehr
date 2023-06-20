from odoo import models , api , fields , _  


class MeetingDetails(models.Model):

    _name = "meeting.details"
    _description ="Meeting Details"

    meeting_id = fields.Many2one('crm.lead', string="Meeting Details")
    partner_id = fields.Many2one('res.partner', string="Customer")
    user_id = fields.Many2one('res.users', string="User Id")
    phone = fields.Char(string="Phone")
    name = fields.Char(string="Lead")
    email_from = fields.Char(string="Email")