
from odoo import models ,fields

class CrmLead(models.Model):

    _inherit= "crm.lead"

    event_id = fields.Many2one("calendar.event",'Meeting Event')

