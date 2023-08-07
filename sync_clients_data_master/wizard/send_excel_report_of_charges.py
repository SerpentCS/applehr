from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class SendEmployeeChargesExcelReport(models.TransientModel):
    _name = "send.excel.report.employee.charges"
    _description = "Send Employee Charges Excel Report"

    start_date = fields.Date(string="Start Date")
    end_date = fields.Date(string="End Date")

    @api.constrains('start_date', 'end_date')
    def _check_date(self):
        for rec in self:
            if rec.end_date:
                if rec.start_date > rec.end_date:
                    raise ValidationError(_(
                        'End Date should be greater than Start Date!'))

    def action_send_email(self):
        if self._context.get('active_model') == 'res.partner':
            partner_rec = self.env['res.partner'].browse(self._context.get('active_ids', []))
            for partner in partner_rec:
                print('\n\n\n partner', partner)

