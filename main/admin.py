from django.contrib import admin
from django.utils.html import format_html
from .models import *
admin.site.register(Product)


from .models import Order, In_Order
from django.contrib import admin

class InOrderInline(admin.TabularInline):
    model = In_Order
    extra = 0
    readonly_fields = ('prodcut', 'quantity')
    can_delete = False


@admin.register(In_Order)
class InOrderAdmin(admin.ModelAdmin):
    list_display = ('order', 'prodcut', 'quantity')
    search_fields = ('order__id', 'prodcut__title')
    readonly_fields = ('order', 'prodcut', 'quantity')


class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'data', 'status', 'total_price_display')
    list_filter = ('data', 'status')
    search_fields = ('id', 'user__username')
    inlines = [InOrderInline]
    ordering = ('-data',)
    readonly_fields = ('id', 'user', 'data', 'total_price_display')

    def total_price_display(self, obj):
        return f"{obj.get_total():,} лей"
    total_price_display.short_description = "Сумма заказа"
