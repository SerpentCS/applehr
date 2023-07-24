# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from werkzeug.urls import url_encode
from odoo import models
from odoo.tools.mimetypes import get_extension


class SlideResource(models.Model):
    _inherit = 'slide.slide.resource'

    def _get_download_url(self):
        self.ensure_one()
        return '#'
        # extension_file_name = get_extension(self.file_name) if self.file_name else ''
        # file_name = self.name if self.name.endswith(extension_file_name) else self.name + extension_file_name
        # return f'/web/content/slide.slide.resource/{self.id}/data?' + url_encode({
        #     'download': 'true',
        #     'filename': file_name
        # })
