from django.urls import path

from . import views

urlpatterns = [
    path("", views.order_list_view, name="order-list"),
    path("create/", views.order_create_view, name="order-create"),
    path("seller/", views.seller_order_list_view, name="seller-order-list"),
    path("<int:order_id>/status/", views.order_update_status_view, name="order-update-status"),
    path("<int:order_id>/", views.order_delete_view, name="order-delete"),
]
