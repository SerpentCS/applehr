from odoo import models , api , fields , _  


class Website(models.Model):

    _inherit = "website"

    appointment_type_id = fields.Many2one('appointment.type', string="Appointment Type")

