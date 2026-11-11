from django import forms
from .models import FoodItem

from .models import FoodActivity


class FoodItemForm(forms.ModelForm):

    class Meta:
        model = FoodItem

        fields = [
            'food_name',
            'category',
            'quantity',
            'unit',
            'unit_price',
            'purchase_date',
            'expiry_date',
            'storage_location',
        ]

        widgets = {
            'food_name': forms.TextInput(attrs={
                'placeholder': 'e.g. Chicken Breast'
            }),
            'quantity': forms.NumberInput(attrs={
                'step': '0.01',
                'min': '0.01'
            }),
            'unit_price': forms.NumberInput(attrs={
                'step': '0.01',
                'min': '0'
            }),
            'purchase_date': forms.DateInput(attrs={
                'type': 'date'
            }),
            'expiry_date': forms.DateInput(attrs={
                'type': 'date'
            }),
        }

    def clean(self):
        cleaned_data = super().clean()

        purchase_date = cleaned_data.get('purchase_date')
        expiry_date = cleaned_data.get('expiry_date')
        quantity = cleaned_data.get('quantity')

        if purchase_date and expiry_date:
            if expiry_date < purchase_date:
                self.add_error(
                    'expiry_date',
                    'Expiry date cannot be before purchase date.'
                )

        if quantity is not None and quantity <= 0:
            self.add_error(
                'quantity',
                'Quantity must be greater than zero.'
            )

        return cleaned_data


class FoodActivityForm(forms.ModelForm):

    class Meta:
        model = FoodActivity

        fields = [
            'food_item',
            'activity_type',
            'quantity',
            'reason',
            'activity_date',
        ]

        widgets = {
            'quantity': forms.NumberInput(attrs={
                'step': '0.01',
                'min': '0.01'
            }),
            'activity_date': forms.DateInput(attrs={
                'type': 'date'
            }),
        }

        labels = {
            'food_item': 'Select Food Item',
            'activity_type': 'Activity Type',
            'quantity': 'Quantity',
            'reason': 'Reason for Waste',
            'activity_date': 'Activity Date',
        }

    def clean(self):
        cleaned_data = super().clean()

        quantity = cleaned_data.get('quantity')
        activity_type = cleaned_data.get('activity_type')
        reason = cleaned_data.get('reason')

        if quantity is not None and quantity <= 0:
            self.add_error(
                'quantity',
                'Quantity must be greater than zero.'
            )

        if activity_type == 'Wasted' and not reason:
            self.add_error(
                'reason',
                'Please select a reason for wasting food.'
            )

        return cleaned_data