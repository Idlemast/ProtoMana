from django.urls import path
from . import views

urlpatterns = [
    # Produits
    path('', views.ProductListView.as_view(), name='product_list'),
    path('produit/<int:pk>/', views.ProductDetailView.as_view(), name='product_detail'),
    path('produit/ajouter/', views.ProductCreateView.as_view(), name='product_create'),
    path('produit/<int:pk>/modifier/', views.ProductUpdateView.as_view(), name='product_update'),
    path('produit/<int:pk>/supprimer/', views.ProductDeleteView.as_view(), name='product_delete'),

    # Catégories
    path('categories/', views.CategoryListView.as_view(), name='category_list'),
    path('categories/ajouter/', views.CategoryCreateView.as_view(), name='category_create'),
    path('categories/<int:pk>/modifier/', views.CategoryUpdateView.as_view(), name='category_update'),
    path('categories/<int:pk>/supprimer/', views.CategoryDeleteView.as_view(), name='category_delete'),

    # Lieux
    path('lieux/', views.LocationListView.as_view(), name='location_list'),
    path('lieux/ajouter/', views.LocationCreateView.as_view(), name='location_create'),
    path('lieux/<int:pk>/modifier/', views.LocationUpdateView.as_view(), name='location_update'),
    path('lieux/<int:pk>/supprimer/', views.LocationDeleteView.as_view(), name='location_delete'),

    # Couleurs
    path('couleurs/', views.ColorListView.as_view(), name='color_list'),
    path('couleurs/ajouter/', views.ColorCreateView.as_view(), name='color_create'),
    path('couleurs/<int:pk>/modifier/', views.ColorUpdateView.as_view(), name='color_update'),
    path('couleurs/<int:pk>/supprimer/', views.ColorDeleteView.as_view(), name='color_delete'),

    # Tailles
    path('tailles/', views.SizeListView.as_view(), name='size_list'),
    path('tailles/ajouter/', views.SizeCreateView.as_view(), name='size_create'),
    path('tailles/<int:pk>/modifier/', views.SizeUpdateView.as_view(), name='size_update'),
    path('tailles/<int:pk>/supprimer/', views.SizeDeleteView.as_view(), name='size_delete'),

    # SKU
    path('sku/', views.SKUListView.as_view(), name='sku_list'),
    path('sku/ajouter/', views.SKUCreateView.as_view(), name='sku_create'),
    path('sku/<int:pk>/modifier/', views.SKUUpdateView.as_view(), name='sku_update'),
    path('sku/<int:pk>/supprimer/', views.SKUDeleteView.as_view(), name='sku_delete'),

    # Stock
    path('stock/', views.StockListView.as_view(), name='stock_list'),
    path('stock/ajouter/', views.StockCreateView.as_view(), name='stock_create'),
    path('stock/<int:pk>/modifier/', views.StockUpdateView.as_view(), name='stock_update'),
    path('stock/<int:pk>/supprimer/', views.StockDeleteView.as_view(), name='stock_delete'),

    # Commandes
    path('commandes/', views.OrderListView.as_view(), name='order_list'),
    path('commandes/<int:pk>/', views.OrderDetailView.as_view(), name='order_detail'),
    path('commandes/ajouter/', views.OrderCreateView.as_view(), name='order_create'),
    path('commandes/<int:pk>/modifier/', views.OrderUpdateView.as_view(), name='order_update'),
    path('commandes/<int:pk>/supprimer/', views.OrderDeleteView.as_view(), name='order_delete'),

    # Clients
    path('clients/', views.CustomerListView.as_view(), name='customer_list'),
    path('clients/ajouter/', views.CustomerCreateView.as_view(), name='customer_create'),
    path('clients/<int:pk>/modifier/', views.CustomerUpdateView.as_view(), name='customer_update'),
    path('clients/<int:pk>/supprimer/', views.CustomerDeleteView.as_view(), name='customer_delete'),

    # Statistiques
    path('statistiques/', views.StatsView.as_view(), name='stats'),
]
