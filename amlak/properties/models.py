from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
# Create your models here.

class Category(models.Model):
    title = models.CharField(max_length=50)
    slug = models.SlugField(max_length=200, unique=True)

    def __str__(self):
        return self.title


class Property(models.Model):
    title = models.CharField(max_length=100, verbose_name=_("عنوان"))
    location = models.CharField(max_length=150, verbose_name=_("آدرس"))
    built_year = models.IntegerField(null=True, verbose_name=_("سال ساخت"))
    class TypeChoices(models.TextChoices):
        apartment = 'آپارتمان',
        house = 'خانه'
    type = models.CharField(max_length=50, choices=TypeChoices, default=TypeChoices.apartment, verbose_name=_("نوع"))
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, verbose_name=_("دسته بندی"))
    status = models.CharField(max_length=100, verbose_name=_("وضعیت"))
    bedroom = models.IntegerField(verbose_name=_("اتاق خواب"))
    bathroom = models.IntegerField( verbose_name=_("دستشویی"))
    description = models.TextField(null=True, verbose_name=_("توضیحات"))
    price = models.IntegerField(verbose_name=_("قیمت"))
    post_date = models.DateTimeField(null=True, verbose_name=_("تاریخ پست"))
    floors = models.IntegerField(null=True, verbose_name=_("تعداد طبقات"))
    parking = models.BooleanField(null=True, verbose_name=_("پارکینگ"))
    lot_area = models.IntegerField(verbose_name=_("متراژ کل"))
    floor_area = models.IntegerField(null=True, verbose_name=_("متراژ سازه"))
    elevator = models.BooleanField(null=True, default=False, verbose_name=_("آسانسور"))
    warehouse = models.BooleanField(null=True, default=False, verbose_name=_("انباری"))
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, verbose_name=_("کاربر"))
    is_approved = models.BooleanField(default=False, verbose_name=_("وضعیت تایید"))


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




