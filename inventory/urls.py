from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),

    path('inventory/', views.inventory_list, name='inventory'),
    path('inventory/add/', views.add_food, name='add_food'),
    path('inventory/edit/<int:pk>/', views.edit_food, name='edit_food'),
    path('inventory/delete/<int:pk>/', views.delete_food, name='delete_food'),

    path(
        'api/analytics/consumption/',
        views.consumption_analytics,
        name='consumption_analytics'
    ),
    path(
        'api/analytics/monthly-savings/',
        views.monthly_savings_analytics,
        name='monthly_savings_analytics'
    ),

    path('activities/', views.activity_list, name='activities'),
    path('activities/add/', views.add_activity, name='add_activity'),
]