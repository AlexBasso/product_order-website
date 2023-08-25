from django import forms
from django.forms import ModelForm

from .models import Product, Order
from django.contrib.auth.models import Group


class CSVImportForm(forms.Form):
    csv_file = forms.FileField()


class GroupForm(ModelForm):
    class Meta:
        model = Group
        fields = ["name"]


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = "name", "description", "price", "discount", 'created_by', 'preview'


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = "delivery_address", "promo_code", "user", "products"


class ProductIMGForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = "name", "description", "price", "discount", 'preview'

    images = forms.ImageField(
        required=False,
        widget=forms.ClearableFileInput(attrs={"multiple": True}),
    )

    # "allow_multiple_selected": True
    # "multiple": True,

    # images = forms.ImageField(
    #     widget=forms.ClearableFileInput(attrs={"multiple": True}),
    # )

# forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}), label='Изображения')






"""

Other options I tried:

"""
# ==================t
# class MultipleFileInput(forms.ClearableFileInput):
#     allow_multiple_selected = True
#
#
#
#     # images = forms.ImageField(
#     #     widget=MultipleFileInput())

# ==================t

#
#
# class MultipleFileInput(forms.ClearableFileInput):
#     allow_multiple_selected = True
#
#
# class MultipleFileField(forms.FileField):
#     def __init__(self, *args, **kwargs):
#         kwargs.setdefault("widget", MultipleFileInput())
#         super().__init__(*args, **kwargs)
#
#     def clean(self, data, initial=None):
#         single_file_clean = super().clean
#         if isinstance(data, (list, tuple)):
#             result = [single_file_clean(d, initial) for d in data]
#         else:
#             result = single_file_clean(data, initial)
#         return result
#
#
# class ProductIMGForm(forms.Form):
#     file_field = MultipleFileField()


# # ==================this worked somewhat, 50/50
# class MultipleFileInput(forms.ClearableFileInput):
#     allow_multiple_selected = True
#
#
# class ProductIMGForm(forms.ModelForm):
#     class Meta:
#         model = Product
#         fields = "name", "description", "price", "discount", 'created_by', 'preview'
#
#     images = forms.ImageField(
#         widget=MultipleFileInput())
# ==================end worked somewhat, 50/50



# class ProductIMGForm(forms.ModelForm):
#     class Meta:
#         model = Product
#         fields = "name", "description", "price", "discount", 'created_by', 'preview'
#
#     images = forms.FileField(
#         widget=forms.ClearableFileInput(attrs={"allow_multiple_selected": True}), required=False
#     )

    # {"multiple": True,
    # {"allow_multiple_selected": True,