from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect
from django.urls import path

from shopapp.admin_mixins import ExportAsCSVMixin
from shopapp.models import Product, Order, ProductImage
from .common import save_csv_products, save_csv_orders
from .forms import CSVImportForm


class OrderInline(admin.TabularInline):
    model = Product.orders.through


class ProductInline(admin.StackedInline):
    model = ProductImage


@admin.action(description='Archive products')
def mark_archived(modeladmin: admin.ModelAdmin, request: HttpRequest, queryset: QuerySet):
    queryset.update(archived=True)


@admin.action(description='Unarchive products')
def mark_unarchived(modeladmin: admin.ModelAdmin, request: HttpRequest, queryset: QuerySet):
    queryset.update(archived=False)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin, ExportAsCSVMixin):
    change_list_template = "shopapp/products_changelist.html"
    actions = [
        mark_archived,
        mark_unarchived,
    ]
    inlines = [
        OrderInline,
        ProductInline,
    ]

    list_display = "pk", "name", "description_short", "price", "discount", "created_at", "created_by", "archived"
    list_display_links = "pk", "name"
    search_fields = "name", "description", "price"
    fieldsets = [
        (None, {
            "fields": ("name", "description"),
        }),
        ("Price options", {
            "fields": ("price", "discount"),
        }),
        ("Images", {
            "fields": ("preview", ),
        }),
        ("Additional Options", {
            "fields": ("archived",),
            "classes": ("collapse",),
        })
    ]

    def description_short(self, obj: Product) -> str:
        if len(obj.description) > 48:
            return obj.description[:48] + ",,,"
        return obj.description

    def import_csv(self, request: HttpRequest) -> HttpResponse:
        if request.method == "GET":
            form = CSVImportForm()
            context = {
                "form": form,
            }
            return render(request, 'admin/csv_form.html', context)
        form = CSVImportForm(request.POST, request.FILES)
        if not form.is_valid():
            context = {
                "form": form,
            }
            return render(request, 'admin/csv_form.html', context, status=400)

        save_csv_products(
            file=form.files["csv_file"].file,
            encoding=request.encoding,
            user=request.user,
        )
        self.message_user(request, "Data from CSV was imported")
        return redirect("..")

    def get_urls(self):
        urls = super().get_urls()
        new_urls = [
            path(
                "import-products-csv/",
                self.import_csv,
                name="import_products_csv",
            ),
        ]
        return new_urls + urls

    def save_model(self, request, obj, form, change):
        print('printing obj ', obj)
        obj.created_by = request.user
        super().save_model(request, obj, form, change)


class ProductThroughInline(admin.TabularInline):
    model = Order.products.through


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin, ExportAsCSVMixin):
    change_list_template = "shopapp/orders_changelist.html"
    inlines = [
        ProductThroughInline,
        # OrderInline,
    ]

    list_display = "pk", "delivery_address", "promo_code", "created_at", "user"
    list_display_links = "pk", "delivery_address"
    search_fields = "delivery_address", "created_at"

    def get_queryset(self, request):
        return Order.objects.select_related("user")

    def import_csv(self, request: HttpRequest) -> HttpResponse:
        if request.method == "GET":
            form = CSVImportForm()
            context = {
                "form": form,
            }
            return render(request, 'admin/csv_form.html', context)
        form = CSVImportForm(request.POST, request.FILES)
        if not form.is_valid():
            context = {
                "form": form,
            }
            return render(request, 'admin/csv_form.html', context, status=400)

        save_csv_orders(
            file=form.files["csv_file"].file,
            encoding=request.encoding,
            user=request.user,
        )
        self.message_user(request, "Data from CSV was imported")
        return redirect("..")

    def get_urls(self):
        urls = super().get_urls()
        new_urls = [
            path(
                "import-orders-csv/",
                self.import_csv,
                name="import_orders_csv",
            ),
        ]
        return new_urls + urls

    def save_model(self, request, obj, form, change):
        print('printing obj ', obj)
        obj.user = request.user
        super().save_model(request, obj, form, change)