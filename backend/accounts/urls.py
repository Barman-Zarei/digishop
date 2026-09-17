from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from . import views

urlpatterns = [
    path("register/", views.register_view, name="register"),
    path("login/", views.login_view, name="login"),
    path("become-seller/", views.become_seller_view, name="become-seller"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
]
