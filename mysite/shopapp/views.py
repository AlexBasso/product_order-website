import logging
import os
from csv import DictWriter

from timeit import default_timer

from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import Group, User
from django.contrib.syndication.views import Feed
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect, JsonResponse, Http404
from django.shortcuts import render, redirect, reverse
from django.core.cache import cache
from django.template.response import SimpleTemplateResponse
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.cache import cache_page
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, OpenApiResponse

from .common import save_csv_products
from shopapp.models import Product, Order, ProductImage
from .forms import GroupForm, ProductIMGForm
from .serializers import ProductSerializer, OrderSerializer

# log = logging.getLogger(__name__)
log = logging.getLogger("info_log")


@extend_schema(description='Product Views CRUD')
class ProductViewSet(ModelViewSet):
    """
    Набор представлений для действий над Product.
    Полный CRUD для сущностей товара.
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [
        SearchFilter,
        DjangoFilterBackend,
        OrderingFilter,
    ]
    search_fields = ["name", "description"]
    filterset_fields = [
        "name",
        "description",
        "price",
        "discount",
        "archived",
    ]
    ordering_fields = [
        "name",
        "price",
        "discount",
    ]

    @extend_schema(
        summary='Get one product by ID',
        description='Retrieves **product**, returns 404 if not found',
        responses={
            200: ProductSerializer,
            400: OpenApiResponse(description='Empty response, product by id not found'),
        }
    )
    def retrieve(self, *args, **kwargs):
        return super().retrieve(*args, **kwargs)

    @action(methods=["get"], detail=False)
    def download_csv(self, request: Request):
        response = HttpResponse(content_type="text/csv")
        filename = "products-export.csv"
        response["Content-Disposition"] = f"attachment; filename={filename}"
        queryset = self.filter_queryset(self.get_queryset())
        fields = [
            "name",
            "description",
            "price",
            "discount",
        ]
        queryset = queryset.only(*fields)
        writer = DictWriter(response, fieldnames=fields)
        writer.writeheader()

        for product in queryset:
            writer.writerow({
                field: getattr(product, field)
                for field in fields
            })
        return response

    @action(
        detail=False,
        methods=["post"],
        parser_classes=[MultiPartParser],
    )
    def upload_csv(self, request: Request) -> Response:
        products = save_csv_products(
            request.FILES["file"].file,
            encoding=request.encoding,
            user=request.user,
        )
        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)

    @method_decorator(cache_page(60 * 1))
    def list(self, *args, **kwargs):
        return super().list(*args, **kwargs)


class OrderViewSet(ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    filter_backends = [
        SearchFilter,
        DjangoFilterBackend,
        OrderingFilter,
    ]
    search_fields = ["name", "description"]
    filterset_fields = [
        "delivery_address",
        "promo_code",
        "user",
        "products",
    ]
    ordering_fields = [
        "delivery_address",
        "promo_code",
        "created_at",
    ]

    def perform_create(self, serializer):
        print('printing user: ', self.request.user)
        serializer.save(user=self.request.user)

    @action(methods=["get"], detail=False)
    def download_csv(self, request: Request):
        response = HttpResponse(content_type="text/csv")
        filename = "orders-export.csv"
        response["Content-Disposition"] = f"attachment; filename={filename}"
        queryset = self.filter_queryset(self.get_queryset())
        fields = [
            "delivery_address",
            "promo_code",
            "created_at",
            "products",
        ]
        queryset = queryset.only(*fields)
        writer = DictWriter(response, fieldnames=fields)
        writer.writeheader()

        for order in queryset:
            writer.writerow({
                field: getattr(order, field)
                for field in fields
            })
        return response


class ShopIndexView(View):

    # @method_decorator(cache_page(60 * 1))
    def get(self, request: HttpRequest) -> HttpResponse:
        products = [
            ('laptop', 1999),
            ('desktop', 2999),
            ('smartphone', 999),
        ]
        context = {
            "time_running": default_timer(),
            "products": products,
            'items': 5,
        }
        # logger_info.debug("Products for shop index: %s ", products)
        log.info("Rendering shop index")
        print('shop index context ', context)
        return render(request, 'shopapp/shop-index.html', context=context)


class GroupListView(View):
    def get(self, request: HttpRequest) -> HttpResponse:
        context = {
            "form": GroupForm(),
            "groups": Group.objects.prefetch_related("permissions").all(),
        }
        return render(request, 'shopapp/groups-list.html', context=context)

    def post(self, request: HttpRequest):
        form = GroupForm(request.POST)
        if form.is_valid():
            form.save()

        return redirect(request.path)


class ProductsListView(ListView):
    """ Product 1"""
    template_name = 'shopapp/products-list.html'
    context_object_name = "products"
    queryset = Product.objects.filter(archived=False)


class ProductDetailsView(DetailView):
    """ Product 2"""
    template_name = 'shopapp/product-details.html'
    model = Product
    context_object_name = "product"


class ProductCreateView(PermissionRequiredMixin, CreateView):
    permission_required = 'shopapp.add_product'
    model = Product
    # fields = "name", "price", "description", "discount", 'preview'
    success_url = reverse_lazy("shopapp:products_list")
    form_class = ProductIMGForm

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        response = super().form_valid(form)

        for image in form.files.getlist("images"):
            ProductImage.objects.create(
                product=self.object,
                image=image,
            )
        return response


class ProductUpdateView(UserPassesTestMixin, UpdateView):
    def test_func(self):
        if self.request.user.is_superuser:
            return True
        return self.request.user.has_perm('shopapp.change_product') \
               and self.get_object().created_by == self.request.user

    model = Product
    # fields = "name", "price", "description", "discount", 'preview'
    template_name_suffix = '_update_form'
    form_class = ProductIMGForm

    def get_success_url(self):
        return reverse(
            'shopapp:product_details',
            kwargs={"pk": self.object.pk},
        )

    def form_valid(self, form):
        response = super().form_valid(form)
        for image in form.files.getlist("images"):
            ProductImage.objects.create(
                product=self.object,
                image=image,
            )
        return response


class ProductDeleteView(DeleteView):
    model = Product
    success_url = reverse_lazy('shopapp:products_list')

    def form_valid(self, form):
        success_url = self.get_success_url()
        self.object.archived = True
        self.object.save()
        return HttpResponseRedirect(success_url)


class OrdersListView(LoginRequiredMixin, ListView):
    queryset = (
        Order.objects.select_related('user').prefetch_related('products')
    )


class OrdersDetailView(PermissionRequiredMixin, DetailView):
    permission_required = 'shopapp.view_order'
    queryset = (
        Order.objects.select_related('user').prefetch_related('products')
    )


class OrderCreateView(CreateView):
    model = Order
    fields = "delivery_address", "promo_code", "products"
    success_url = reverse_lazy("shopapp:orders_list")

    def form_valid(self, form):
        form.instance.user = self.request.user
        response = super().form_valid(form)
        return response


class OrderUpdateView(UpdateView):
    model = Order
    fields = "delivery_address", "promo_code", "user", "products"
    template_name_suffix = '_update_form'

    def get_success_url(self):
        return reverse(
            'shopapp:order_details',
            kwargs={"pk": self.object.pk},
        )


class OrderDeleteView(DeleteView):
    model = Order
    success_url = reverse_lazy('shopapp:orders_list')


class ProductsDataExportView(View):
    def get(self, request: HttpRequest) -> JsonResponse:
        cache_key = "products_data_export"
        products_data = cache.get(cache_key)
        if products_data is None:
            products = Product.objects.order_by('pk').all()
            products_data = [
                {
                    'pk': product.pk,
                    'name': product.name,
                    'price': product.price,
                    'archived': product.archived,

                }
                for product in products
            ]
            cache.set(cache_key, products_data, 30)
            # elem = products_data[0]
            # name = elem["name"]
            # print("name", name)

        return JsonResponse({'products': products_data})


class OrderDataExportView(UserPassesTestMixin, View):
    def test_func(self):
        if self.request.user.is_staff:
            return True
        return False

    def get(self, request: HttpRequest) -> JsonResponse:
        orders = Order.objects.order_by('pk').all()
        orders_data = [
            {
                'pk': order.pk,
                'name': order.delivery_address,
                'price': order.promo_code,
                'user_id': order.user_id,
                'products_list': [
                    {"id": product.pk}
                    for product in order.products.all()
                ]
            }
            for order in orders
        ]
        return JsonResponse({'orders': orders_data})


class LatestProductsFeed(Feed):
    title = "Shop Products (latest)"
    description = "Update on changes and additions of shop products"
    link = reverse_lazy("shopapp:products_list")

    def items(self):
        return (
            Product.objects
            .filter(created_at__isnull=False)
            .order_by("-created_at")[:5]
        )

    def item_title(self, item: Product):
        return item.name

    def item_description(self, item: Product):
        return item.description[:200]


class UserOrdersListView(LoginRequiredMixin, ListView):
    template_name = 'shopapp/user_order.html'
    context_object_name = "orders"

    def get_queryset(self):
        try:
            self.owner = User.objects.get(id=self.kwargs['pk'])
        except:
            raise Http404('<h1>404 Error, USER with #{pk} does not exist</h1>'.format(pk=self.kwargs['pk']))
        return Order.objects.filter(
            user=User.objects.get(id=self.kwargs['pk'])
        ).select_related('user').prefetch_related('products')

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data['owner'] = self.owner
        return data


class UserOrdersDataExportView(View):

    def get(self, request: HttpRequest, **kwargs) -> JsonResponse:
        try:
            self.owner = User.objects.get(id=self.kwargs['pk'])
        except:
            raise Http404('<h1>404 Error, USER with #{pk} does not exist</h1>'.format(pk=self.kwargs['pk']))
        cache_key = "user_orders_data_export" + "_{}".format(self.kwargs['pk'])
        user_orders_data = cache.get(cache_key)
        if user_orders_data is None:

            orders = Order.objects.filter(
                user=User.objects.get(id=self.kwargs['pk'])
            ).select_related('user').prefetch_related('products').order_by('pk')

            user_orders_data = OrderSerializer(orders, many=True)
            cache.set(cache_key, user_orders_data, 30)
            print("Cache was empty, setting cache in dir: ", str(os.path.abspath(cache_key)))
        else:
            print("Cache was found in dir: ", str(os.path.abspath(cache_key)))

        return JsonResponse({'orders': user_orders_data.data})

