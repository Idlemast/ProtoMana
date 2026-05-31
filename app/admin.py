from django.contrib import admin
from .models import Category, Product, Color, Size, SKU, Location, Stock, Customer, Order, OrderItem

class SKUInline(admin.TabularInline):
    model = SKU
    extra = 1

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1

class StockInline(admin.TabularInline):
    model = Stock
    extra = 1

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent')
    search_fields = ('name',)
    list_filter = ('parent',)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'created_at')
    search_fields = ('name', 'description')
    list_filter = ('category', 'created_at')
    inlines = [SKUInline]

@admin.register(Color)
class ColorAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Size)
class SizeAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(SKU)
class SKUAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'size', 'color')
    search_fields = ('product__name', 'size__name', 'color__name')
    list_filter = ('size', 'color')
    inlines = [StockInline]

@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'address')
    search_fields = ('name', 'address')
    list_filter = ('type',)
    inlines = [StockInline]

@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ('location', 'sku', 'quantity')
    search_fields = ('sku__product__name', 'location__name')
    list_filter = ('location',)

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('firstname', 'lastname', 'email')
    search_fields = ('firstname', 'lastname', 'email')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'location', 'status', 'created_at')
    search_fields = ('customer__firstname', 'customer__lastname', 'id')
    list_filter = ('status', 'location', 'created_at')
    inlines = [OrderItemInline]

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'sku', 'quantity', 'price')
    search_fields = ('order__id', 'sku__product__name')
