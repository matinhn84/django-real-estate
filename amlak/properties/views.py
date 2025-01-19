from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.views.generic import ListView

from .models import Property
# Create your views here.

def get_property():
    properties = Property.objects.prefetch_related('images').all().order_by('-post_date')
    context = {
        'properties': properties,
    }
    return context

def index_view(request):
    context_properties = get_property()
    context = { **context_properties }
    return render(request, 'properties/index.html', context)

def properties_view(request):
    context_properties = get_property()
    context = { **context_properties }
    return render(request, 'properties/property_list.html', context)


def property_single_view(request, slug):
    property = get_object_or_404(Property, slug=slug)
    relateds = Property.objects.filter(type=property.type).exclude(id=property.id)[:2]
    context_properties = get_property()
    context = {
         **context_properties,
         'property': property,
         'relateds':relateds,
    }
    return render(request, 'properties/property_single.html', context)



    

