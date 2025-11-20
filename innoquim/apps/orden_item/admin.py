from django.contrib import admin
from .models import OrdenItem


@admin.register(OrdenItem)
class OrdenItemAdmin(admin.ModelAdmin):
    list_display = ["id", "order", "product", "quantity", "unit", "created_at"]
    list_filter = ["order", "product"]
    search_fields = ["order__order_code", "product__name"]
    readonly_fields = ["created_at", "updated_at"]
