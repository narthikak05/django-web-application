from django.contrib import admin
from django.urls import path
from .import views
app_name='newapp'
urlpatterns=[
    path('',views.index),
    path('items/',views.ProductListView.as_view(),name='items'),
    #path('items/add/<int:id>',views.add_product,name='add_product'),
    path('items/<int:pk>/',views.ProductDetailView.as_view(),name='item_detail'),
    path('items/add/',views.ProductCreateView.as_view(),name='add_product'),
    path('items/update/<int:pk>',views.ProductUpdateView.as_view(),name='update_product'),
    path('items/delete/<int:pk>',views.ProductDeleteView.as_view(),name='delete_product'),
    path('items/mylistings',views.my_listings,name='my_listings'), 
    path('items/success/',views.PaymentSuccessView.as_view(),name='success'),
    path('items/failed/',views.PaymentFailedView.as_view(),name='failed'),
    path('api/checkout-session/<int:id>',views.create_checkout_session,name='api_checkout_session'),
]
#path('items/',views.items,name='items'),
#path('items/<int:id>/',views.item_detail,name='item_detail'),
#path('items/update/<int:id>',views.update_product,name='update_product'),
#path('items/delete/<int:id>',views.delete_product,name='delete_product'),
#path('items/mylistings',views.my_listings,name='mylistings'),
