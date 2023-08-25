from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from .models import Product, Order


class ProductSitemap(Sitemap):
    changefreq = "always"
    priority = 0.5

    def items(self):
        return Product.objects.order_by("-created_at")

    def lastmod(self, obj: Product):
        return obj.created_at


class OrderSitemap(Sitemap):
    changefreq = "always"
    priority = 0.5

    def items(self):
        return Order.objects.order_by("-created_at")

    def lastmod(self, obj: Product):
        return obj.created_at


class StaticViewSitemap(Sitemap):
    priority = 0.9
    changefreq = "always"

    def items(self):
        return ["shopapp:index"]

    def location(self, item):
        return reverse(item)