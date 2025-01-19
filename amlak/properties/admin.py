from django.contrib import admin
from .models import Property, Image
# Register your models here.

class PropertyImageInline(admin.TabularInline):
    model = Image
    extra = 1

class PropertyAdmin(admin.ModelAdmin):
    list_display = ('__str__','user', 'post_date')
    inlines = [PropertyImageInline]

admin.site.register(Property, PropertyAdmin)
admin.site.register(Image)

