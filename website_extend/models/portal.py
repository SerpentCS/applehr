# -*- coding: utf-8 -*-

from odoo.http import request
from odoo.addons.portal.controllers import portal


class BalancePortal(portal.CustomerPortal):

    def _prepare_home_portal_values(self, counters):
        print('COUNTER WWWWW\n',counters)
        values = super()._prepare_home_portal_values(counters)
        if 'balance_count' in counters:
            my_user = request.env.user
            values['balance_count'] = my_user.partner_id.balance
        if 'balance_record' in counters:
            my_user = request.env.user
            values['balance_record'] = my_user.partner_id.name
        return values

