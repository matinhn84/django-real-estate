from django import forms
from .models import Property, Image


class PropertyForm(forms.ModelForm):
    class Meta:
        model = Property
        fields = [
            'title', 'location', 'built_year', 'category',
            'status', 'bedroom', 'bathroom', 'description', 'price',
            'floors', 'parking', 'lot_area', 'floor_area', 'elevator',
            'warehouse', 'equipment', 'user', 'is_approved', 'is_special'
        ]

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(PropertyForm, self).__init__(*args, **kwargs)

        if user and not user.is_superuser:
            self.fields.pop('user')
            self.fields.pop('is_approved')
            self.fields.pop('is_special')


class PropertyImageForm(forms.ModelForm):
    class Meta:
        model = Image
        fields = ['image']
