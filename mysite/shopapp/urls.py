from django.urls import path, include
from django.views.decorators.cache import cache_page
from rest_framework.routers import DefaultRouter

from .views import ShopIndexView, GroupListView, ProductDetailsView, ProductsListView, OrdersListView, \
    OrdersDetailView, ProductCreateView, ProductUpdateView, ProductDeleteView, OrderCreateView, OrderUpdateView, \
    OrderDeleteView, ProductsDataExportView, OrderDataExportView, ProductViewSet, OrderViewSet, LatestProductsFeed, \
    UserOrdersListView, UserOrdersDataExportView


app_name = 'shopapp'

routers = DefaultRouter()
routers.register("products", ProductViewSet)
routers.register("orders", OrderViewSet)


urlpatterns = [
    path('', ShopIndexView.as_view(), name='index'),
    path('api', include(routers.urls)),
    path('groups/', GroupListView.as_view(), name='groups_list'),
    path('products/', ProductsListView.as_view(), name='products_list'),
    path('products/export', ProductsDataExportView.as_view(), name='products-export'),
    path('products/create', ProductCreateView.as_view(), name='product_create'),
    path('products/<int:pk>/', ProductDetailsView.as_view(), name='product_details'),
    path('products/<int:pk>/update', ProductUpdateView.as_view(), name='product_update'),
    path('products/<int:pk>/archive', ProductDeleteView.as_view(), name='product_delete'),
    path('products/latest/feed/', LatestProductsFeed(), name='products-feed'),

    path('orders/', OrdersListView.as_view(), name='orders_list'),
    path('orders/export', OrderDataExportView.as_view(), name='orders-export'),
    path('orders/create/', OrderCreateView.as_view(), name='order_create'),
    path('orders/<int:pk>/', OrdersDetailView.as_view(), name='order_details'),
    path('orders/<int:pk>/update', OrderUpdateView.as_view(), name='order_update'),
    path('orders/<int:pk>/confirm-delete', OrderDeleteView.as_view(), name='order_confirm_delete'),

    path('users/<int:pk>/orders', UserOrdersListView.as_view(), name='user_orders_list'),
    path('users/<int:pk>/orders/export', UserOrdersDataExportView.as_view(), name='user_orders_list_export'),

]
