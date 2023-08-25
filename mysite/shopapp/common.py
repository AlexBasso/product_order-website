from csv import DictReader
from io import TextIOWrapper

from shopapp.models import Product, Order


def save_csv_products(file, encoding, user):
    csv_file = TextIOWrapper(
        file,
        encoding,
    )
    reader = DictReader(csv_file)
    products = [
        Product(
            **row,
            created_by=user)
        for row in reader
    ]
    Product.objects.bulk_create(products)
    return products


def save_csv_orders(file, encoding, user):
    csv_file = TextIOWrapper(
        file,
        encoding,
    )
    reader = DictReader(csv_file)
    orders = []
    products_m2m = []
    for row in reader:
        orders.append(Order(
            delivery_address=row['delivery_address'],
            promo_code=row['promo_code'],
            user=user))
        if ',' in row['products']:
            row['products'] = row['products'].split(",")
        products_m2m.append(row['products'])

    Order.objects.bulk_create(orders)
    for counter, order in enumerate(orders):
        if isinstance(products_m2m[counter], list):
            for prod_id in products_m2m[counter]:
                order.products.add(prod_id)
        else:
            order.products.add(products_m2m[counter])

    return orders
