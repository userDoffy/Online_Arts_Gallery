from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User

class Painting(models.Model):

    CATEGORY_CHOICES = [
        ("Bookmark", "Bookmark"),
        ("Landscape", "Landscape"),
        ("Portrait", "Portrait"),
        ("Sketch", "Sketch"),
    ]
    
    FACE_CHOICES = [(1,"1"), (2,"2"), (3,"3")] 

    name = models.CharField(max_length=200)
    canvas_size = models.CharField(max_length=100)  
    photo = models.ImageField(upload_to='media/paintings/')
    category = models.CharField(max_length=10, choices=CATEGORY_CHOICES, default="Bookmark")
    faces = models.IntegerField(choices=FACE_CHOICES, blank=True, null=True) 
    price = models.DecimalField(max_digits=10, decimal_places=2)
    released_date = models.DateField()

    def clean(self):
        if self.category == "Portrait" and self.faces is None:
            raise ValidationError("For 'Portrait' category, 'faces' must be specified.")
        elif self.category != "Portrait" and self.faces is not None:
            raise ValidationError("'Faces' can only be set for 'Portrait' category.")
    
    def __str__(self):
        return self.name

class CartItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="cart")
    painting = models.ForeignKey('Painting', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.painting.name} - {self.user.username}"