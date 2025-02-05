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
    predicted_price = models.DecimalField(max_digits=10, decimal_places=2)
    owner_name = models.CharField(max_length=255, null=True, blank=True)  # New field
    date_listed = models.DateField(null=True, blank=True)  # New field
    description = models.TextField(null=True, blank=True)  # New field
    # images = models.ImageField(null=True, blank=True, upload_to=upload_path)  # New field

   
   
class PropertyImage(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="property_images/")