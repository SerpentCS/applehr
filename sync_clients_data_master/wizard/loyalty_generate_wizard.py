from odoo import _, api, fields, models


class LoyaltyGenerateWizard(models.TransientModel):
    _inherit = "loyalty.generate.wizard"

    def generate_coupons(self):
        # Add balance in customers balance history and customers
        for wizard in self:
            customers = wizard._get_partners() or range(wizard.coupon_qty)
            for partner in customers:
                balance_values = {
                    'description': 'Balance added using eWallet',
                    'partner_id': partner.id,
                    'credit': wizard.points_granted,
                    'debit': 0.0,
                    'date': fields.Date.today(),
                }
                new_balance_rec = self.env['balance.history'].create(balance_values)
                partner.balance += wizard.points_granted
                new_balance_rec.write({
                    'closing_balance': partner.balance
                })
        return super().generate_coupons()


    def generate_coupons(self):
        # overwrite method to add balance in customers balance history and create only new customer eWallets line.
        if any(not wizard.program_id for wizard in self):
            raise ValidationError(_("Can not generate coupon, no program is set."))
        if any(wizard.coupon_qty <= 0 for wizard in self):
            raise ValidationError(_("Invalid quantity."))
        coupon_create_vals = []
        loyalty_card_obj = self.env['loyalty.card']
        partner_obj = self.env['res.partner']
        for wizard in self:
            customers = wizard._get_partners() or range(wizard.coupon_qty)
            for partner in customers:
                coupon_create_vals.append(wizard._get_coupon_values(partner))
        for coupon_vals in coupon_create_vals:
            partner_id = self.env['res.partner'].browse(coupon_vals.get('partner_id'))
            loyalty_card_rec = loyalty_card_obj.search([
                ('partner_id', '=', partner_id.id)
            ], limit=1)
            if loyalty_card_rec:
                loyalty_card_rec.points += self.points_granted
                # customers balance history.
                balance_values = {
                    'description': 'Balance added using eWallet',
                    'partner_id': partner_id.id,
                    'credit': self.points_granted,
                    'debit': 0.0,
                    'date': fields.Date.today(),
                }
                new_balance_rec = self.env['balance.history'].create(balance_values)
                partner_id.balance += self.points_granted
                new_balance_rec.write({
                    'closing_balance': partner_id.balance
                })
            else:
                loyalty_card_obj.create(coupon_vals)
                # customers balance history.
                balance_values = {
                    'description': 'Balance added using eWallet',
                    'partner_id': partner_id.id,
                    'credit': self.points_granted,
                    'debit': 0.0,
                    'date': fields.Date.today(),
                }
                new_balance_rec = self.env['balance.history'].create(balance_values)
                partner_id.balance += self.points_granted
                new_balance_rec.write({
                    'closing_balance': partner_id.balance
                })
        return True
