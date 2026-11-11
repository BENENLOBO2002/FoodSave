from datetime import timedelta
from django.http import JsonResponse
from django.db.models import (
    Sum,
    Count,
    DecimalField,
    ExpressionWrapper,
    F,
)
from django.db.models.functions import TruncMonth
from django.utils import timezone
from .models import FoodItem, FoodActivity
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q
from .forms import FoodItemForm
from django.db import transaction
from .forms import FoodItemForm, FoodActivityForm

def dashboard(request):
    return render(request, 'inventory/dashboard.html')


def consumption_analytics(request):

    period = request.GET.get('period', '30')

    activities = FoodActivity.objects.all()

    if period != 'all':

        try:
            days = int(period)

            if days not in [7, 30, 90]:
                raise ValueError

            today = timezone.localdate()
            start_date = today - timedelta(days=days - 1)

            activities = activities.filter(
                activity_date__gte=start_date,
                activity_date__lte=today
            )

        except ValueError:
            return JsonResponse(
                {'error': 'Invalid reporting period'},
                status=400
            )

    # Count activities by type instead of adding incompatible units
    results = activities.values('activity_type').annotate(
        total=Count('id')
    )

    consumed = 0
    wasted = 0

    for item in results:

        if item['activity_type'] == 'Consumed':
            consumed = item['total']

        elif item['activity_type'] == 'Wasted':
            wasted = item['total']

    return JsonResponse({
        'period': period,
        'consumed': consumed,
        'wasted': wasted
    })


def monthly_savings_analytics(request):

    today = timezone.localdate()

    # Show the current month and previous 11 months
    first_month = (
        today.replace(day=1) -
        timedelta(days=335)
    ).replace(day=1)

    activities = FoodActivity.objects.filter(
        activity_type='Consumed',
        activity_date__gte=first_month,
        activity_date__lte=today
    )

    # Calculate quantity multiplied by its historical unit price
    food_value = ExpressionWrapper(
        F('quantity') * F('unit_price'),
        output_field=DecimalField(
            max_digits=18,
            decimal_places=2
        )
    )

    results = (
        activities
        .annotate(month=TruncMonth('activity_date'))
        .values('month')
        .annotate(total_saved=Sum(food_value))
        .order_by('month')
    )

    monthly_data = [
        {
            'month': item['month'].strftime('%Y-%m'),
            'saved': float(item['total_saved'] or 0)
        }
        for item in results
    ]

    return JsonResponse({
        'currency': 'EUR',
        'monthly_data': monthly_data
    })


def inventory_list(request):
    today = timezone.localdate()

    food_items = FoodItem.objects.all()

    # Search by food name
    search_query = request.GET.get('search', '').strip()

    if search_query:
        food_items = food_items.filter(
            food_name__icontains=search_query
        )

    # Filter by category
    category = request.GET.get('category', '')

    if category:
        food_items = food_items.filter(category=category)

    # Filter by expiry status
    status = request.GET.get('status', '')

    if status == 'expired':
        food_items = food_items.filter(expiry_date__lt=today)

    elif status == 'expiring':
        food_items = food_items.filter(
            expiry_date__gte=today,
            expiry_date__lte=today + timedelta(days=3)
        )

    elif status == 'fresh':
        food_items = food_items.filter(
            expiry_date__gt=today + timedelta(days=3)
        )

    # Sorting
    sort = request.GET.get('sort', 'expiry_date')

    allowed_sort_options = [
        'expiry_date',
        '-expiry_date',
        'food_name',
        '-food_name',
        'quantity',
        '-quantity',
    ]

    if sort not in allowed_sort_options:
        sort = 'expiry_date'

    food_items = food_items.order_by(sort)

    # Attach expiry status to each item
    for item in food_items:
        days_remaining = (item.expiry_date - today).days

        if days_remaining < 0:
            item.expiry_status = 'expired'
        elif days_remaining <= 3:
            item.expiry_status = 'expiring'
        else:
            item.expiry_status = 'fresh'

    context = {
        'food_items': food_items,
        'search_query': search_query,
        'selected_category': category,
        'selected_status': status,
        'selected_sort': sort,
        'categories': FoodItem.CATEGORY_CHOICES,
    }

    return render(request, 'inventory/inventory.html', context)


def add_food(request):
    if request.method == 'POST':
        form = FoodItemForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, 'Food item added successfully.')
            return redirect('inventory')
    else:
        form = FoodItemForm()

    return render(request, 'inventory/food_form.html', {
        'form': form,
        'page_title': 'Add Food Item'
    })


def edit_food(request, pk):
    food_item = get_object_or_404(FoodItem, pk=pk)

    if request.method == 'POST':
        form = FoodItemForm(request.POST, instance=food_item)

        if form.is_valid():
            form.save()
            messages.success(request, 'Food item updated successfully.')
            return redirect('inventory')
    else:
        form = FoodItemForm(instance=food_item)

    return render(request, 'inventory/food_form.html', {
        'form': form,
        'page_title': 'Edit Food Item'
    })


def delete_food(request, pk):
    food_item = get_object_or_404(FoodItem, pk=pk)

    if request.method == 'POST':
        food_name = food_item.food_name
        food_item.delete()

        messages.success(
            request,
            f'{food_name} was deleted from inventory.'
        )

        return redirect('inventory')

    return render(request, 'inventory/confirm_delete.html', {
        'food_item': food_item
    })


def add_activity(request):

    if request.method == 'POST':
        form = FoodActivityForm(request.POST)

        if form.is_valid():

            try:
                with transaction.atomic():

                    # Lock the selected food item while updating stock
                    food_item = FoodItem.objects.select_for_update().get(
                        pk=form.cleaned_data['food_item'].pk
                    )

                    quantity = form.cleaned_data['quantity']

                    # Prevent recording more food than available
                    if quantity > food_item.quantity:
                        form.add_error(
                            'quantity',
                            f'Only {food_item.quantity} {food_item.unit} available.'
                        )

                    else:
                        # Deduct the consumed or wasted quantity
                        food_item.quantity -= quantity
                        food_item.save()

                        # Create the activity record
                        activity = form.save(commit=False)
                        activity.food_item = food_item
                        activity.save()

                        messages.success(
                            request,
                            'Food activity recorded and inventory updated.'
                        )

                        return redirect('activities')

            except FoodItem.DoesNotExist:
                form.add_error(
                    'food_item',
                    'The selected food item no longer exists.'
                )

    else:
        form = FoodActivityForm()

    return render(request, 'inventory/activity_form.html', {
        'form': form,
        'page_title': 'Record Food Activity'
    })


def activity_list(request):

    activities = FoodActivity.objects.all().order_by(
        '-activity_date',
        '-created_at'
    )

    # Filter by activity type
    activity_type = request.GET.get('type', '')

    if activity_type in ['Consumed', 'Wasted']:
        activities = activities.filter(
            activity_type=activity_type
        )
    else:
        activity_type = ''

    # Search by food name
    search_query = request.GET.get('search', '').strip()

    if search_query:
        activities = activities.filter(
            food_name__icontains=search_query
        )

    context = {
        'activities': activities,
        'selected_type': activity_type,
        'search_query': search_query,
    }

    return render(
        request,
        'inventory/activities.html',
        context
    )