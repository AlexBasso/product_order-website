from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _


def product_preview_directory_path(instance: "Product", filename: str) -> str:
    return 'products/product_{pk}/preview/{filename}'.format(
        pk=instance.pk,
        filename=filename,
    )


class Product(models.Model):
    """
    Модель Product представляет товар,
    который можно продовать в магазине.

    Заказы тут: :model:`shopapp.Order`
    """
    class Meta:
        ordering = ["name", "price"]
        verbose_name = _('Product')
        verbose_name_plural = _('Products')

    name = models.CharField(max_length=100, db_index=True)
    description = models.TextField(null=False, blank=True, db_index=True)
    price = models.DecimalField(default=0, max_digits=8, decimal_places=2)
    discount = models.PositiveSmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    archived = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    preview = models.ImageField(null=True, blank=True, upload_to=product_preview_directory_path)

    def __str__(self) -> str:
        return f"Product( pk= {self.pk}, name= {self.name!r})"

    def get_absolute_url(self):
        return reverse("shopapp:product_details", kwargs={"pk": self.pk})


def product_image_directory_path(instance: "ProductImages", filename: str) -> str:
    return 'products/product_{pk}/images/{filename}'.format(
        pk=instance.product.pk,
        filename=filename,
    )


class ProductImage(models.Model):
    product = models.ForeignKey(Product, null=True, blank=True, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(null=True, blank=True, upload_to=product_image_directory_path)
    description = models.CharField(max_length=200, null=False, blank=True)


class Order(models.Model):
    class Meta:
        verbose_name = _('Order')
        verbose_name_plural = _('Orders')

    delivery_address = models.TextField(null=True, blank=True)
    promo_code = models.CharField(max_length=20, null=False, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    products = models.ManyToManyField(Product, related_name='orders')
    receipt = models.FileField(null=True, blank=True, upload_to='orders/receipts')

    def __str__(self) -> str:
        return f"Order ( pk= {self.pk}, delivery address= {self.delivery_address!r})"

    def get_absolute_url(self):
        return reverse("shopapp:order_details", kwargs={"pk": self.pk})
