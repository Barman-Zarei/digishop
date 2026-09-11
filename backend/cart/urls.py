from django.urls import path

from . import views

urlpatterns = [
    path("", views.cart_list_view, name="cart-list"),
    path("add/", views.cart_add_view, name="cart-add"),
    path("<int:item_id>/", views.cart_update_view, name="cart-update"),
    path("<int:item_id>/remove/", views.cart_remove_view, name="cart-remove"),
]
