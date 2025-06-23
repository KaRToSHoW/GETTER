# main/urls.py
from django.urls import path
from .views import (
    CategoryListView, ProductListView, OrderDetailView, 
    add_to_wishlist, remove_from_wishlist, check_wishlist, 
    get_cart, add_to_cart, remove_from_cart, ProductDetailView, 
    ReviewListCreateView, get_favorites, user_orders, check_user_purchased_product,
    popular_wishlist_products, user_activity, FilteredProductListView,
    new_products, popular_products, recent_reviews, create_order,
    send_order_notification, peexam_list
)

urlpatterns = [
    path('categories/', CategoryListView.as_view(), name='category-list'),
    path('products/', ProductListView.as_view(), name='product-list'),
    path('products/<int:pk>/', ProductDetailView.as_view(), name='product-detail'),
    path('products/<int:product_id>/check-purchased/', check_user_purchased_product, name='check-purchased'),
    path('products/<int:product_id>/reviews/', ReviewListCreateView.as_view(), name='review-list-create'),
    path('products/<int:product_id>/reviews/<int:review_id>/', ReviewListCreateView.as_view(), name='review-detail'),
    path('products/popular-wishlist/', popular_wishlist_products, name='popular-wishlist-products'),
    path('products/new/', new_products, name='new-products'),
    path('products/popular/', popular_products, name='popular-products'),
    path('wishlist/add/', add_to_wishlist, name='add-to-wishlist'),
    path('wishlist/remove/<int:product_id>/', remove_from_wishlist, name='remove-from-wishlist'),
    path('wishlist/check/', check_wishlist, name='check-wishlist'),
    path('products/favorites/', get_favorites, name='get-favorites'),
    path('cart/', get_cart, name='get-cart'),
    path('cart/add/', add_to_cart, name='add-to-cart'),
    path('cart/remove/<int:item_id>/', remove_from_cart, name='remove-from-cart'),
    path('orders/<int:pk>/', OrderDetailView.as_view(), name='order_detail'),
    path('orders/create/', create_order, name='create-order'),
    path('orders/<int:order_id>/notify/', send_order_notification, name='send-order-notification'),
    path('user/orders/', user_orders, name='user-orders'),
    path('user/<int:user_id>/activity/', user_activity, name='user-activity'),
    path('api/user-activity/<int:user_id>/', user_activity, name='user_activity'),
    path('api/user-activity/', user_activity, name='user_activity'),
    path('products/search/advanced/', FilteredProductListView.as_view(), name='advanced-product-search'),
    path('recent-reviews/', recent_reviews, name='recent_reviews'),
    path('peexam/', peexam_list, name='peexam-list'),
]