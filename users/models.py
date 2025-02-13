from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings


class CustomUser(AbstractUser):
    # username = models.TextField(max_length=255)
    email = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    pass



def upload_path(instance, filename):
    return '/'.join(['images', str(instance.address)]) + filename

class Property(models.Model):
    location = models.CharField(max_length=255)
    address = models.TextField()
    size = models.CharField(max_length=50)
    bedrooms = models.IntegerField()
    bathrooms = models.IntegerField()
    actual_price = models.IntegerField(default=0)
    owner_name = models.CharField(max_length=255, null=True, blank=True)
    date_listed = models.DateField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    # images = models.ImageField(null=True, blank=True, upload_to=upload_path)  # New field

   
   
class PropertyImage(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="property_images/")



class Bid(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    )
    
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name="bids")
    bidder = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    notified = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Bid of {self.amount} on {self.property}"