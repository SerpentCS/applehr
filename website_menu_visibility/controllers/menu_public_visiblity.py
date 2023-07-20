from odoo import models, http, _
from odoo.addons.http_routing.models.ir_http import slug
from werkzeug.utils import redirect
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.addons.website.models.ir_http import sitemap_qs2dom
from odoo.addons.http_routing.models.ir_http import slug
from odoo.addons.website_slides.controllers.main import WebsiteSlides


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

class WebsiteSale(WebsiteSale):
    def sitemap_shop(env, rule, qs):
        if not qs or qs.lower() in '/shop':
            yield {'loc': '/shop'}

        Category = env['product.public.category']
        dom = sitemap_qs2dom(qs, '/shop/category', Category._rec_name)
        dom += env['website'].get_current_website().website_domain()
        for cat in Category.search(dom):
            loc = '/shop/category/%s' % slug(cat)
            if not qs or qs.lower() in loc:
                yield {'loc': loc}

    @http.route([
        '/shop',
        '/shop/page/<int:page>',
        '/shop/category/<model("product.public.category"):category>',
        '/shop/category/<model("product.public.category"):category>/page/<int:page>',
    ], type='http', auth="user", website=True, sitemap=sitemap_shop)
    def shop(self, page=0, category=None, search='', min_price=0.0, max_price=0.0, ppg=False, **post):
        return super().shop(page, category, search, min_price, max_price, ppg, **post)
    
    @http.route(['/shop/<model("product.template"):product>'], type='http', auth="user", website=True, sitemap=True)
    def product(self, product, category='', search='', **kwargs):
        return super().product(product, category, search)

    @http.route(['/shop/cart'], type='http', auth="user", website=True, sitemap=False)
    def cart(self, access_token=None, revive='', **post):
        return super().cart(access_token=None, revive='', **post)
        

class WebsiteSlides(WebsiteSlides):

    @http.route('/slides', type='http', auth="user", website=True, sitemap=True)
    def slides_channel_home(self, **post):
        return super().slides_channel_home(**post)

    def sitemap_slide(env, rule, qs):
        Channel = env['slide.channel']
        dom = sitemap_qs2dom(qs=qs, route='/slides/', field=Channel._rec_name)
        dom += env['website'].get_current_website().website_domain()
        for channel in Channel.search(dom):
            loc = '/slides/%s' % slug(channel)
            if not qs or qs.lower() in loc:
                yield {'loc': loc}

    @http.route([
        '/slides/<model("slide.channel"):channel>',
        '/slides/<model("slide.channel"):channel>/page/<int:page>',
        '/slides/<model("slide.channel"):channel>/tag/<model("slide.tag"):tag>',
        '/slides/<model("slide.channel"):channel>/tag/<model("slide.tag"):tag>/page/<int:page>',
        '/slides/<model("slide.channel"):channel>/category/<model("slide.slide"):category>',
        '/slides/<model("slide.channel"):channel>/category/<model("slide.slide"):category>/page/<int:page>',
    ], type='http', auth="user", website=True, sitemap=sitemap_slide)
    def channel(self, channel, category=None, tag=None, page=1, slide_category=None, uncategorized=False, sorting=None, search=None, **kw):
        return super().channel(channel, category, tag, page, slide_category, uncategorized, sorting, search, **kw)
    

    @http.route(['/slides/all', '/slides/all/tag/<string:slug_tags>'], type='http', auth="user", website=True, sitemap=True)
    def slides_channel_all(self, slide_category=None, slug_tags=None, my=False, **post):
        return super().slides_channel_all(  slide_category=None, slug_tags=None, my=False, **post)