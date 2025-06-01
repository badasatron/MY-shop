
from django.urls import path,include
from django.conf.urls.static import static
from django.conf import settings
from .views import *
urlpatterns = [
	path('',main,name="main"),
	path('add/<int:product_id>/',add,name="add"),
	path('cart',cart,name="cart"),
	path('increase/<int:cart_id>/<int:product_id>/',increase,name="increase"),
	path('decrease/<int:cart_id>/<int:product_id>/',decrease,name="decrease"),
	path('checkout',checkout,name='checkout'),
	path('checkoutcont/<int:order_id>/',check_continue,name="checkoutcont"),
	path('orders/',orders_list,name="order_list"),
	path('order/<int:order_id>/',order_detail,name="order_detail"),
	# path('category/<int:category_id>/', products_by_category, name='products_by_category'),
# urls.py
	path('category/<int:category_id>/', products_by_category, name='products_by_category'),
	path('product/<int:product_id>/', product_detail, name='product_detail'),
	# path('product/<int:pk>/', product_detail, name='product_detail')
	path('search/', search, name='search'),
	path('categories/', all_categories, name='all_categories'),
]
urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)