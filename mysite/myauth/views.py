from random import random

from django.contrib.auth.decorators import login_required, permission_required, user_passes_test
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.contrib.auth.views import LogoutView
from django.http import HttpRequest, HttpResponse, JsonResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, reverse
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse_lazy
from django.views import View
from django.views.decorators.cache import cache_page
from django.views.generic import TemplateView, CreateView, UpdateView, ListView, DetailView
from django.utils.translation import gettext_lazy as _, ngettext

from myauth.models import Profile


class HelloView(View):
    welcome_message = _('Hello World! text')

    def get(self, request: HttpRequest) -> HttpResponse:
        items_str = request.GET.get('items') or 0
        items = int(items_str)
        products_line = ngettext(
            "one product",
            "{count} products",
            items,
        )
        products_line = products_line.format(count=items)
        return HttpResponse(
            f"<h1>{self.welcome_message}</h1>"
            f"\n<h2>{products_line}</h2>"
        )


class AboutMeView(TemplateView):
    template_name = "myauth/about-me.html"


class RegisterView(CreateView):
    form_class = UserCreationForm
    template_name = 'myauth/register.html'
    success_url = reverse_lazy('myauth:about-me')

    def form_valid(self, form):
        response = super().form_valid(form)
        Profile.objects.create(user=self.object)
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password1')
        user = authenticate(self.request, username=username, password=password)
        login(request=self.request, user=user)
        return response


def login_view(request: HttpRequest) -> HttpResponse:
    if request.method == "GET":
        if request.user.is_authenticated:
            return redirect('/admin/')

        return render(request, 'myauth/login.html')

    username = request.POST['username']
    password = request.POST['password']

    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        return redirect('/admin/')

    return render(request, 'myauth/login.html', {"error": 'invalid login credentials'})


def logout_view(request: HttpRequest) -> HttpResponse:
    logout(request)
    return redirect(reverse('myauth:login'))


class MyLogoutView(LogoutView):
    next_page = reverse_lazy('myauth:login')


@user_passes_test(lambda u: u.is_superuser)
def set_cookie_view(request: HttpRequest) -> HttpResponse:
    response = HttpResponse('Cookie set')
    response.set_cookie('fizz', 'buzz', max_age=3600)
    return response

@cache_page(60 * 2)
def get_cookie_view(request: HttpRequest) -> HttpResponse:
    value = request.COOKIES.get('fizz', 'default value')
    return HttpResponse(f'Cookie value: {value!r} + {random()}')


@permission_required('myauth.view_profile', raise_exception=True)
def set_session_view(request: HttpRequest) -> HttpResponse:
    request.session['foobar'] = 'spameggs'
    return HttpResponse('Session set!')


@login_required
def get_session_view(request: HttpRequest) -> HttpResponse:
    value = request.session.get('foobar', 'default')
    return HttpResponse(f'Session value: {value!r}')


class FooBarView(View):
    def get(self, request: HttpRequest) -> JsonResponse:
        return JsonResponse({'foo': 'bar', 'spam': 'eggs'})


class ChangeAvatarView(UpdateView):
    model = Profile
    fields = "bio", "avatar"
    template_name_suffix = '_update_form'

    def get_success_url(self):
        return reverse(
            'myauth:about-me'
        )


class ProfileListView(ListView):
    template_name = 'myauth/profiles-list.html'
    context_object_name = "profiles"

    def get_queryset(self):
        return User.objects.all()


class ProfileDetailsView(DetailView):
    template_name = 'myauth/profile-details.html'
    context_object_name = "profile"
    model = Profile


class ChangeAvatarIsStaffView(UserPassesTestMixin, UpdateView):
    def test_func(self):
        if self.request.user.is_staff:
            return True

    model = Profile
    fields = ("avatar",)
    template_name = 'myauth/avatar_update_form.html'

    def get_success_url(self):
        pk = self.kwargs["pk"]
        return reverse(
            'myauth:profile-details', kwargs={'pk': pk}
        )
