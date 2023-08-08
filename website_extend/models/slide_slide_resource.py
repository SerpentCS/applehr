# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import re
from werkzeug.urls import url_encode
from odoo import models, api, fields
from odoo.tools.mimetypes import get_extension
from odoo.addons.web_editor.tools import get_video_embed_code
from markupsafe import Markup
from werkzeug import urls


class SlideResource(models.Model):
    _inherit = 'slide.slide.resource'

    YOUTUBE_VIDEO_ID_REGEX = r'^.*(youtu.be\/|v\/|u\/\w\/|embed\/|watch\?v=|&v=)([^#&?]*).*'
    GOOGLE_DRIVE_DOCUMENT_ID_REGEX = r'(^https:\/\/docs.google.com|^https:\/\/drive.google.com).*\/d\/([^\/]*)'
    VIMEO_VIDEO_ID_REGEX = r'\/\/(player.)?vimeo.com\/(?:[a-z]*\/)*([0-9]{6,11})\/?([0-9a-z]{6,11})?[?]?.*'

    def _get_link_resources_url(self, link):
        if link:
            video_source_type = False
            youtube_match = re.match(self.YOUTUBE_VIDEO_ID_REGEX, link) if link else False
            if youtube_match and len(youtube_match.groups()) == 2 and len(youtube_match.group(2)) == 11:
                query_params = urls.url_parse(link).query
                query_params = query_params + '&theme=light' if query_params else 'theme=light'
                return ("//www.youtube-nocookie.com/embed/%s?%s") % (youtube_match.group(2), query_params)
            if not video_source_type:
                match = re.match(self.GOOGLE_DRIVE_DOCUMENT_ID_REGEX, link)
                if match and len(match.groups()) == 2:
                    google_drive_id = match.group(2)
                    return "//drive.google.com/file/d/%s/preview" % (google_drive_id)
            vimeo_match = re.search(self.VIMEO_VIDEO_ID_REGEX, link) if link else False
            if not video_source_type and vimeo_match and len(vimeo_match.groups()) == 3:
                video_source_type = 'vimeo'
        return link

    def _get_download_url(self):
        self.ensure_one()
        return '#'
        # extension_file_name = get_extension(self.file_name) if self.file_name else ''
        # file_name = self.name if self.name.endswith(extension_file_name) else self.name + extension_file_name
        # return f'/web/content/slide.slide.resource/{self.id}/data?' + url_encode({
        #     'download': 'true',
        #     'filename': file_name
        # })
    
    def _get_file_resources_url(self):
        self.ensure_one()
        #return '#'
        extension_file_name = get_extension(self.file_name) if self.file_name else ''
        file_name = self.name if self.name.endswith(extension_file_name) else self.name + extension_file_name
        return f'/web/content/slide.slide.resource/{self.id}/data?' + url_encode({
            'filename': file_name
        })
