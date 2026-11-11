from django.contrib import admin
from .models import FoodItem, FoodActivity


@admin.register(FoodItem)
class FoodItemAdmin(admin.ModelAdmin):

    list_display = (
        'food_name',
        'category',
        'quantity',
        'unit',
        'unit_price',
        'expiry_date',
        'storage_location'
    )

    list_filter = ('category', 'storage_location', 'unit')
    search_fields = ('food_name',)
    ordering = ('expiry_date',)


@admin.register(FoodActivity)
class FoodActivityAdmin(admin.ModelAdmin):

    list_display = (
        'food_name',
        'activity_type',
        'quantity',
        'unit',
        'unit_price',
        'activity_date'
    )

    list_filter = ('activity_type', 'reason', 'activity_date')
    search_fields = ('food_name',)
    date_hierarchy = 'activity_date'