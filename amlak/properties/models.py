from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
# Create your models here.

class Category(models.Model):
    title = models.CharField(max_length=50)
    slug = models.SlugField(max_length=200, unique=True)

    def __str__(self):
        return self.title


class Property(models.Model):
    title = models.CharField(max_length=100)
    slug = models.SlugField(max_length=200, unique=True, blank=True, null=True)
    location = models.CharField(max_length=150)
    built_year = models.IntegerField(null=True)
    class TypeChoices(models.TextChoices):
        apartment = 'آپارتمان',
        house = 'خانه'
    type = models.CharField(max_length=50, choices=TypeChoices, default=TypeChoices.apartment)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True)
    status = models.CharField(max_length=100)
    bedroom = models.IntegerField()
    bathroom = models.IntegerField()
    description = models.TextField(null=True)
    price = models.IntegerField()
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    post_date = models.DateTimeField(auto_now_add=True, auto_now=False, null=True) 
    floors = models.IntegerField(null=True)
    parking = models.BooleanField(null=True)
    lot_area = models.IntegerField()
    floor_area = models.IntegerField(null=True)
    elevator = models.BooleanField(null=True, default=False)
    warehouse = models.BooleanField(null=True, default=False)
    is_approved = models.BooleanField(default=False)


    def save(self, *args, **kwargs):
        if not self.slug:  # Generate slug only if it doesn't already exist
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def thumbnail(self):
        first_image = self.images.first()
        return first_image.image.url if first_image else None


    def __str__(self):
        return f"{self.lot_area}متر in {self.location}"


class Image(models.Model):
    property = models.ForeignKey(Property, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='property/')

    def __str__(self):
        return f"image for {self.property.title}"
    


# CONTACT MODEL 
class Contact(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(max_length=254)
    subject = models.CharField(max_length=100)
    message = models.TextField()

    def __str__(self):
        return f"{self.name} : {self.subject}"


class Message(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='messages')
    content = models.TextField()
    is_read = models.BooleanField(default=False)  # وضعیت خواندن پیام
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message for {self.user.username} - Read: {self.is_read}"
