from django.contrib import admin
from .models import InventoryItem, InventoryCategory

@admin.register(InventoryCategory)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'icon']

@admin.register(InventoryItem)
class ItemAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'quantity', 'condition', 'location']
    list_filter = ['category', 'condition']
    search_fields = ['name', 'serial_number', 'location']
