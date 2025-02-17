from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User

class Painting(models.Model):
    # Define category and face options
    CATEGORY_CHOICES = [
        ("Bookmark", "Bookmark"),
        ("Landscape", "Landscape"),
        ("Portrait", "Portrait"),
        ("Sketch", "Sketch"),
    ]
    
    FACE_CHOICES = [(i, str(i)) for i in range(1, 4)]  # Allow 1 to 3 faces

    # Painting attributes
    name = models.CharField(max_length=200)
    canvas_size = models.CharField(max_length=100)  # E.g., "12x16 inches"
    photo = models.ImageField(upload_to='media/paintings/')
    category = models.CharField(max_length=10, choices=CATEGORY_CHOICES, default="Bookmark")
    faces = models.IntegerField(choices=FACE_CHOICES, blank=True, null=True)  # Optional unless Portrait
    price = models.DecimalField(max_digits=10, decimal_places=2)
    released_date = models.DateField()

    # Validation logic
    def clean(self):
        if self.category == "Portrait" and self.faces is None:
            raise ValidationError("For 'Portrait' category, 'faces' must be specified.")
        if self.category != "Portrait" and self.faces is not None:
            raise ValidationError("'Faces' can only be set for the 'Portrait' category.")
    
    # String representation for admin and shell
    def __str__(self):
        return self.name

class CartItem(models.Model):
    # Define user and painting relations
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="cart")
    painting = models.ForeignKey('Painting', on_delete=models.CASCADE)

    # Other cart item details
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    # Payment and delivery statuses
    STATUS_CHOICES = [
        ("unpaid", "Unpaid"),
        ("unpaid(COD)", "Unpaid(COD)"),
        ("paid", "Paid"),
    ]
    DELIVERY_CHOICES = [
        ("pending", "Pending"),
        ("completed", "Completed"),
    ]
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default="unpaid")
    delivery = models.CharField(max_length=10, choices=DELIVERY_CHOICES, default="pending")

    # String representation
    def __str__(self):
        return f"{self.painting.name} - {self.user.username}"