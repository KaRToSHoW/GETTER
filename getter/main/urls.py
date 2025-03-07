# main/urls.py
from django.urls import path
from .views import CategoryListView, ProductListView, OrderDetailView, add_to_wishlist, remove_from_wishlist, check_wishlist, get_cart, add_to_cart, remove_from_cart, ProductDetailView, ReviewListCreateView

urlpatterns = [
    path('categories/', CategoryListView.as_view(), name='category-list'),
    path('products/', ProductListView.as_view(), name='product-list'),
    path('products/<int:pk>/', ProductDetailView.as_view(), name='product-detail'),
    path('products/<int:product_id>/reviews/', ReviewListCreateView.as_view(), name='review-list-create'),
    path('wishlist/add/', add_to_wishlist, name='add-to-wishlist'),
    path('wishlist/remove/<int:product_id>/', remove_from_wishlist, name='remove-from-wishlist'),
    path('wishlist/check/', check_wishlist, name='check-wishlist'),
    path('cart/', get_cart, name='get-cart'),
    path('cart/add/', add_to_cart, name='add-to-cart'),
    path('cart/remove/<int:item_id>/', remove_from_cart, name='remove-from-cart'),
    path('orders/<int:pk>/', OrderDetailView.as_view(), name='order_detail'),
]