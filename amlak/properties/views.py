from django.core.paginator import Paginator
from django.shortcuts import render
from django.contrib import messages
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404
from django.db.models import Count
from django.views.generic import ListView, CreateView

from .models import Property, Category, Contact
# Create your views here.


def index_view(request):
    properties = Property.objects.prefetch_related('images').all().order_by('-post_date')[:6]
    context = {
        'properties': properties,
    }
    return render(request, 'properties/index.html', context)

def properties_view(request):

    # filter properties
    title = request.GET.get('title', '')
    location = request.GET.get('location', '')
    type = request.GET.get('type', '')
    status = request.GET.get('status', '')
    min_bedroom = request.GET.get('min_bedroom', '')
    min_bathroom = request.GET.get('min_bathroom', '')
    min_price = request.GET.get('min_price', '')
    max_price = request.GET.get('max_price', '')
    min_area = request.GET.get('min_area', '')
    max_area = request.GET.get('max_area', '')

    properties = Property.objects.prefetch_related('images').all().order_by('-post_date')

    if title:
        properties = properties.filter(title__icontains=title)
    if location:
        properties = properties.filter(location__icontains=location)
    if type:
        properties = properties.filter(type__icontains=type)
    if status:
        properties = properties.filter(status__icontains=status)
    if min_bedroom:
        properties = properties.filter(bedroom__gte=min_bedroom)
    if min_bathroom:
        properties = properties.filter(bathroom__gte=min_bathroom)
    if min_price:
        properties = properties.filter(price__gte=min_price)
    if max_price:
        properties = properties.filter(price__lte=max_price)
    if min_area:
        properties = properties.filter(lot_area__gte=min_area)
    if max_area:
        properties = properties.filter(lot_area__lte=max_area)

    # PAGINATION
    # paginator = Paginator(properties, 6)
    # page_number = request.GET.get('page')
    # page_obj = paginator.get_page(page_number)

    context = {
        'properties':properties,
        # 'page_obj': page_obj, pagination
    }
    return render(request, 'properties/property_list.html', context)


def property_single_view(request, slug):
    property = get_object_or_404(Property, slug=slug)
    relateds = Property.objects.filter(type=property.type).exclude(id=property.id)[:2]
    categories = Category.objects.annotate(property_count=Count('property'))
    context = {
         'property': property,
         'relateds':relateds,
         'categories': categories,
    }
    return render(request, 'properties/property_single.html', context)


# PAGES *ABOUT *CONTACT US VIEW

class AboutView(ListView):
    model = Property
    template_name = 'properties/about.html'


class ContactCreate(CreateView):
    model = Contact
    fields = "__all__"
    template_name = 'properties/contact.html'
    success_url = reverse_lazy('properties:contact')

    def form_valid(self, form):
        messages.success(self.request, "پیام ارسال شد")
        return super().form_valid(form)