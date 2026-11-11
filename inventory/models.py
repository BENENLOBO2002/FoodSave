from django.db import models


class FoodItem(models.Model):

    CATEGORY_CHOICES = [
        ('Fruits', 'Fruits'),
        ('Vegetables', 'Vegetables'),
        ('Dairy', 'Dairy'),
        ('Meat', 'Meat'),
        ('Seafood', 'Seafood'),
        ('Grains', 'Grains'),
        ('Beverages', 'Beverages'),
        ('Other', 'Other'),
    ]

    UNIT_CHOICES = [
        ('kg', 'Kilograms'),
        ('g', 'Grams'),
        ('litres', 'Litres'),
        ('ml', 'Millilitres'),
        ('pieces', 'Pieces'),
    ]

    STORAGE_CHOICES = [
        ('Fridge', 'Fridge'),
        ('Freezer', 'Freezer'),
        ('Pantry', 'Pantry'),
    ]

    food_name = models.CharField(max_length=100)

    category = models.CharField(
        max_length=30,
        choices=CATEGORY_CHOICES
    )

    quantity = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    unit = models.CharField(
        max_length=20,
        choices=UNIT_CHOICES
    )

    # Price for one unit of measurement, e.g. €3 per kg
    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    purchase_date = models.DateField()

    expiry_date = models.DateField()

    storage_location = models.CharField(
        max_length=20,
        choices=STORAGE_CHOICES
    )

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.food_name


class FoodActivity(models.Model):

    ACTIVITY_CHOICES = [
        ('Consumed', 'Consumed'),
        ('Wasted', 'Wasted'),
    ]

    REASON_CHOICES = [
        ('Spoilage', 'Spoilage'),
        ('Expired', 'Expired'),
        ('Over-purchasing', 'Over-purchasing'),
        ('Preparation waste', 'Preparation waste'),
        ('Other', 'Other'),
    ]

    food_item = models.ForeignKey(
        FoodItem,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='activities'
    )

    food_name = models.CharField(max_length=100)

    activity_type = models.CharField(
        max_length=20,
        choices=ACTIVITY_CHOICES
    )

    quantity = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    unit = models.CharField(
        max_length=20,
        choices=FoodItem.UNIT_CHOICES
    )

    reason = models.CharField(
        max_length=30,
        choices=REASON_CHOICES,
        blank=True
    )

    activity_date = models.DateField()

    # Snapshot of the product price when the activity is recorded
    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):

        # Copy product details when a new activity is created
        if not self.pk and self.food_item_id:
            self.food_name = self.food_item.food_name
            self.unit = self.food_item.unit
            self.unit_price = self.food_item.unit_price

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.food_name} - {self.activity_type}"