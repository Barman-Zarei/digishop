from django.urls import path

from . import views

urlpatterns = [
    path("", views.product_list_view, name="product-list"),
    path("mine/", views.seller_product_list_view, name="seller-product-list"),
    path("create/", views.product_create_view, name="product-create"),
    path("<int:product_id>/", views.product_detail_view, name="product-detail"),
    path("<int:product_id>/update/", views.product_update_view, name="product-update"),
    path("<int:product_id>/delete/", views.product_delete_view, name="product-delete"),
]
