from django.urls import path

from . import views

app_name = "orders"

urlpatterns = [
    path('orders/', views.OrderView.as_view(), name='orders'),
    path('order/edit/<slug:order_id>/', views.UpdateOrderView.as_view(), name='edit'),
    path('order/remove/<slug:order_id>/', views.remove_order, name='remove'),
    path('order/create/<slug:order_id>/', views.CreateOrderView.as_view(), name='create'),
    path('order/item/create', views.add_order_item),
    path('stocks_and_costs/', views.stocks_and_costs),
    path('order/export/pdf/<slug:order_id>/', views.ExportPDFView.as_view(), name='export-pdf'),
    path('order/export/xlsx/<slug:order_id>/', views.ExportXLSXView.as_view(), name='export-xlsx'),
    path('order/import/xlsx/', views.import_xlsx, name='import-xlsx'),
]
