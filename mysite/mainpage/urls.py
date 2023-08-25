from django.urls import path
from .views import MainpageView

app_name = 'mainpage'

urlpatterns = [
    path('', MainpageView.as_view(), name='index'),

]
