from odoo import fields, models, api, _


class WebsiteMenu(models.Model):
    _inherit = 'website.menu'

    def _compute_visible(self):
        super()._compute_visible()
        for menu in self:
            if not menu.is_visible:
                return
            if menu.url == '/shop' or menu.url == '/slides':
                if self.env.user and self.env.user.has_group('base.group_public'):
                    menu.is_visible = False