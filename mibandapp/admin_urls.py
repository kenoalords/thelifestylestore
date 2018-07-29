from django.urls import path
from mibandapp.views import DashboardIndex, OrderSingleView, OrderAllView, ProductList, ProductAddSingle, ProductDelete, ProductEdit

urlpatterns = [
    path('', DashboardIndex.as_view(), name="dashboard"),
    path('orders/', OrderAllView.as_view(), name='orders'),
    path('order/<uuid>', OrderSingleView.as_view(), name='view_order'),
    path('products/', ProductList.as_view(), name='products'),
    path('product/add', ProductAddSingle.as_view(), name="add_product"),
    path('product/<id>/delete', ProductDelete.as_view(), name="delete_product"),
    path('product/<id>/edit', ProductEdit.as_view(), name="edit_product"),
]
