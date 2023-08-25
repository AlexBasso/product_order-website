from typing import Sequence

from django.contrib.auth.models import User
from django.core.management import BaseCommand
from django.db import transaction

from shopapp.models import Order, Product


class Command(BaseCommand):
    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write('Create order with products')
        user = User.objects.get(username='alex')
        # products: Sequence[Product] = Product.objects.all()
        # products: Sequence[Product] = Product.objects.defer("description", "price", "created_at").all()
        products: Sequence[Product] = Product.objects.only("id", "name").all()
        order, create = Order.objects.get_or_create(
            delivery_address='ul Ivanova, 33',
            promo_code='promo3',
            user=user,
        )
        for product in products:
            order.products.add(product)
        order.save()
        self.stdout.write(f'Created order {order}')
        self.stdout.write(self.style.SUCCESS(f'Created order {order}'))

