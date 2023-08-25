from string import ascii_letters
from random import choices

from django.conf import settings
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from shopapp.models import Product, Order


class ProductCreateViewTestCase(TestCase):
    def setUp(self) -> None:
        self.product_name = ''.join(choices(ascii_letters, k=10))
        Product.objects.filter(name=self.product_name).delete()

    def test_create_prod(self):
        response = self.client.post(
            reverse('shopapp:product_create'),
            {
                'name': self.product_name,
                'price': '123.34',
                'description': "A good table",
                'discount': "10",
            }
        )
        self.assertRedirects(response, reverse('shopapp:products_list'))
        self.assertTrue(
            Product.objects.filter(name=self.product_name).exists()
        )


class ProductDetailsViewTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        user = User.objects.create_user("john", "lennon@thebeatles.com", "johnpassword")
        cls.product = Product.objects.create(name='Best product', created_by=user)

    @classmethod
    def tearDownClass(cls):
        cls.product.delete()

    # def setUp(self) -> None:
    #     self.product = Product.objects.create(name='Best product', created_by_id=1)
    #
    # def tearDown(self) -> None:
    #     self.product.delete()

    def test_get_product(self):
        print('running test1')
        response = self.client.get(
            reverse('shopapp:product_details', kwargs={'pk': self.product.pk})
        )
        self.assertEqual(response.status_code, 200)

    def test_get_product_and_check_content(self):
        response = self.client.get(
            reverse('shopapp:product_details', kwargs={'pk': self.product.pk})
        )
        self.assertContains(response, self.product.name)


class ProductListViewTestCase(TestCase):
    fixtures = [
        'product-fixtures.json',
    ]

    # def test_products(self):
    #     response = self.client.get(reverse('shopapp:products_list'))
    #     for product in Product.objects.filter(archive=False).all():
    #         self.assertContains(response, product)

    # def test_products(self):
    #     response = self.client.get(reverse('shopapp:products_list'))
    #     products = Product.objects.filter(archive=False).all()
    #     products_ = response.context['products']
    #     for p, p_ in zip(products, products_):
    #         self.assertEqual(p.pk, p_.pk)

    def test_products(self):
        response = self.client.get(reverse('shopapp:products_list'))
        self.assertQuerySetEqual(
            qs=Product.objects.filter(archive=False).all(),
            values=(p.pk for p in response.context['products']),
            transform=lambda p: p.pk,
        )
        self._assert_template_used(response, 'shopapp/products-list.html')


class OrdersListViewTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.credentials = dict(username='bob_test', password='1234')
        cls.user = User.objects.create_user(**cls.credentials)

    @classmethod
    def tearDownClass(cls):
        cls.user.delete()

    # def setUp(self) -> None:
    #     self.client.login(**self.credentials)

    def setUp(self) -> None:
        self.client.force_login(self.user)

    def test_orders_view(self):
        resource = self.client.get(reverse('shopapp:orders_list'))
        self.assertContains(resource, 'Orders')

    def test_orders_view_not_authenticated(self):
        self.client.logout()
        response = self.client.get(reverse('shopapp:orders_list'))
        # self.assertRedirects(response, str(settings.LOGIN_URL))
        self.assertEqual(response.status_code, 302)
        self.assertIn(str(settings.LOGIN_URL), response.url)


class ProductsExportViewTestCase(TestCase):
    fixtures = [
        'product-fixtures.json',
        'order-fixtures.json',
        'auth-fixtures.json',
    ]

    def test_get_products_view(self):
        response = self.client.get(reverse('shopapp:products-export'))
        self.assertEqual(response.status_code, 200)
        products = Product.objects.order_by('pk').all()
        expected_data = [
            {
                'pk': product.pk,
                'name': product.name,
                'price': str(product.price),
                'archived': product.archived,

             }
            for product in products
        ]
        products_data = response.json()
        self.assertEqual(products_data['products'], expected_data)


class OrderDetailViewTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.credentials = dict(username='bob_test', password='1234')
        cls.user = User.objects.create_user(**cls.credentials)
        cls.user.user_permissions.set([32])

    @classmethod
    def tearDownClass(cls):
        cls.user.delete()

    def setUp(self) -> None:
        self.client.login(**self.credentials)

        self.order = Order.objects.create(
            delivery_address='Best order streat',
            promo_code='+150%price',
            user=self.user,
        )

    def tearDown(self) -> None:
        self.order.delete()

    def test_get_order_code(self):
        response = self.client.get(
            reverse('shopapp:order_details', kwargs={'pk': self.order.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.order.delivery_address)
        self.assertContains(response, self.order.promo_code)
        self.assertContains(response, self.order.pk)


class OrdersExportTestCase(TestCase):
    fixtures = [
        'product-fixtures.json',
        'order-fixtures.json',
        'auth-fixtures.json',
    ]

    @classmethod
    def setUpClass(cls):
        cls.credentials = dict(username='staff_test', password='1234')
        cls.user = User.objects.create_user(**cls.credentials)
        cls.user.is_staff = True
        cls.user.save()

    @classmethod
    def tearDownClass(cls):
        cls.user.delete()

    def setUp(self) -> None:
        self.client.login(**self.credentials)

    def test_check_status_and_body(self):
        response = self.client.get(reverse('shopapp:orders-export'))
        self.assertEqual(response.status_code, 200)
        orders = Order.objects.order_by('pk').all()
        expected_body = [
            {
                'pk': order.pk,
                'name': order.delivery_address,
                'price': order.promo_code,
                'archived': order.user_id,
                'products_list': [
                    {"id": product.pk}
                    for product in order.products.all()
                ]
            }
            for order in orders
        ]
        orders_data = response.json()
        self.assertEqual(orders_data['orders'], expected_body)
