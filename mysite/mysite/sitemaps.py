from BlogApp.sitemap import BlogSitemap
from shopapp.sitemap import ProductSitemap, OrderSitemap, StaticViewSitemap

sitemaps = {
    "blogs": BlogSitemap,
    "shop/product": ProductSitemap,
    "shop/order": OrderSitemap,
    "shop": StaticViewSitemap,
}