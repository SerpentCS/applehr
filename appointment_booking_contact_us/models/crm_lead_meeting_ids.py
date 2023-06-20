from odoo import models ,fields, api ,_

class CrmMeetings(models.Model):

    _inherit= "crm.lead"

    meeting_ids = fields.One2many("meeting.details","meeting_id",string="Meeting Ids")


    


