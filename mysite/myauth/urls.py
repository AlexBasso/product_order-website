from django.contrib.auth.views import LoginView
from django.urls import path

# from .views import login_view, logout_view
from myauth.views import get_cookie_view, set_cookie_view, set_session_view, get_session_view, MyLogoutView, \
    AboutMeView, RegisterView, FooBarView, ChangeAvatarView, ProfileListView, ProfileDetailsView, \
    ChangeAvatarIsStaffView, HelloView

app_name = 'myauth'

urlpatterns = [
    path('login/',
         LoginView.as_view(
             template_name='myauth/login.html',
             redirect_authenticated_user=True),
         name='login'),
    path('hello/', HelloView.as_view(), name='hello'),
    path('logout/', MyLogoutView.as_view(), name='logout'),
    path('cookie/get/', get_cookie_view, name='cookie-get'),
    path('cookie/set/', set_cookie_view, name='cookie-set'),
    path('session/get/', get_session_view, name='session-get'),
    path('session/set/', set_session_view, name='session-set'),

    path("about-me/", AboutMeView.as_view(), name="about-me"),
    path('register/', RegisterView.as_view(), name='register'),
    path('change-avatar/<int:pk>/', ChangeAvatarView.as_view(), name='change-avatar'),

    path("profiles-list/", ProfileListView.as_view(), name="profiles-list"),
    path("profiles-details/<int:pk>/", ProfileDetailsView.as_view(), name="profile-details"),
    path('profiles-details/<int:pk>/change-avatar-staff', ChangeAvatarIsStaffView.as_view(),
         name='change-avatar-staff'),

    path('foo-bar/', FooBarView.as_view(), name='foo-bar')
    # path('login/', login_view, name='login'),
    # path('logout/', logout_view, name='logout'),

]
