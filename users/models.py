from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from decimal import Decimal
from datetime import datetime, timedelta
from django.utils import timezone


class CustomUser(AbstractUser):
    # Add any custom fields you need
    email = models.EmailField(unique=True)
    
    # Override the username field to allow spaces
    username = models.CharField(
        max_length=150,
        unique=True,
        help_text='Required. 150 characters or fewer. Letters and spaces only.',
        error_messages={
            'unique': "A user with that username already exists.",
        },
    )

    password = models.CharField(max_length=255)
    pass

    def save(self, *args, **kwargs):
        # Ensure username is in title case
        if self.username:
            self.username = self.username.title()
        super().save(*args, **kwargs)



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

    @property
    def is_bidding_closed(self):
        if not self.date_listed:
            return False
        
        # Convert date_listed to datetime if it's just a date
        if isinstance(self.date_listed, datetime):
            listing_date = self.date_listed
        else:
            listing_date = datetime.combine(self.date_listed, datetime.min.time())
            listing_date = timezone.make_aware(listing_date)
        
        # Calculate end date (2 days after listing)
        end_date = listing_date + timedelta(days=2)
        return timezone.now() > end_date

   
   
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
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    notified = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Bid of {self.amount} on {self.property}"

    def save(self, *args, **kwargs):
        # Ensure amount is Decimal before saving
        if isinstance(self.amount, str):
            self.amount = Decimal(self.amount.replace(',', ''))
        super().save(*args, **kwargs)