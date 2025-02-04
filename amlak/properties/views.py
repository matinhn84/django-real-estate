from django.shortcuts import render, redirect
from django.contrib import messages
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404
from django.http import Http404
from django.db.models import Count, Q
from django.contrib.auth.models import User
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone

from django.views.generic import ListView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Property, Category, Contact, Message, Image
from .forms import PropertyForm
# Create your views here.


def index_view(request):
    properties = Property.objects.prefetch_related('images').filter(is_approved=True).order_by('-post_date')[:6]
    special_properties = Property.objects.none()
    if request.user.is_staff:
        special_properties = Property.objects.prefetch_related('images').filter(is_approved=True, is_special=True).order_by('-post_date')
    last_tree_properties = properties[:3]
    context = {
        'properties': properties,
        'special_properties' : special_properties,
        'last_tree_properties':last_tree_properties,
    }
    return render(request, 'properties/index.html', context)

def properties_view(request):
    # Get filter parameters
    title = request.GET.get('title', '')
    location = request.GET.get('location', '')
    type = request.GET.get('type', '')
    category_name = request.GET.get('category_name', '')
    status = request.GET.get('status', '')
    min_bedroom = int(request.GET.get('min_bedroom', 0)) if request.GET.get('min_bedroom') else 0
    min_bathroom = int(request.GET.get('min_bathroom', 0)) if request.GET.get('min_bathroom') else 0
    min_price = int(request.GET.get('min_price', 0)) if request.GET.get('min_price') else 0
    max_price = int(request.GET.get('max_price', 0)) if request.GET.get('max_price') else 0
    min_area = int(request.GET.get('min_area', 0)) if request.GET.get('min_area') else 0
    max_area = int(request.GET.get('max_area', 0)) if request.GET.get('max_area') else 0

    # Base query
    if request.user.is_staff or request.user.is_superuser:
        properties = Property.objects.prefetch_related('images').filter(is_approved=True)
    else:
        properties = Property.objects.prefetch_related('images').filter(is_approved=True, is_special=False)

    # Apply filters dynamically
    if title:
        properties = properties.filter(title__icontains=title)
    if location:
        properties = properties.filter(location__icontains=location)
    if type:
        properties = properties.filter(type__exact=type)  # Use `exact` for non-text fields
    if category_name:
        properties = properties.filter(category_name__icontains=category_name)
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

    # Order the results
    properties = properties.order_by('-post_date')

    context = {
        'properties': properties,
    }
    return render(request, 'properties/property_list.html', context)



def property_single_view(request, pk):
    property = get_object_or_404(Property.objects.filter(is_approved=True), pk=pk)
    relateds = Property.objects.filter(type=property.type).exclude(id=property.id)[:2]
    categories = Category.objects.annotate(
        property_count=Count('property', filter=Q(property__is_approved=True))
    ).filter(property_count__gt=0)
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

# register user
class UserCreate(CreateView):
    model = User
    fields = ['username', 'password', 'first_name', 'last_name']
    success_url = '/login'

    def form_valid(self, form):
        user = form.save(commit=False)
        user.set_password(form.cleaned_data['password'])
        user.save()
        return super().form_valid(form)



# Dashboard views

# update user and notification sign
class UpdateUser(LoginRequiredMixin,UpdateView):
    model = User
    template_name = 'cms/information_form.html'
    fields = ['username', 'first_name', 'last_name', 'email']
    success_url = reverse_lazy('properties:information')

    def get_object(self, queryset=None):
        # Fetch the User instance of the currently logged-in user
        return get_object_or_404(User, pk=self.request.user.pk)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add unread messages to the context
        context['unread_messages'] = self.request.user.messages.filter(is_read=False)
        return context

# user posts
class PostsView(LoginRequiredMixin,ListView):
    model = Property
    template_name = 'cms/posts.html'
    context_object_name = 'posts'

    def get_queryset(self):
        queryset = Property.objects.prefetch_related('images').all().order_by('-post_date')
        if self.request.user.is_superuser:
            return queryset
        return queryset.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current_date = timezone.now()

        for post in context['posts']:
            if post.post_date:
                post.days_difference = (current_date - post.post_date).days
        return context


@receiver(pre_save, sender=Property)
def save_previous_approval_status(sender, instance, **kwargs):

    if instance.pk:
        previous_instance = Property.objects.get(pk=instance.pk)
        instance.previous_is_approved = previous_instance.is_approved
    else:
        instance.previous_is_approved = False  # مقدار پیش‌فرض برای موارد جدید

@receiver(post_save, sender=Property)
def create_message_on_post_approval(sender, instance, created, **kwargs):
    # بررسی کنید که تایید شده باشد و مقدار قبلی تایید نشده باشد
    if instance.is_approved and not instance.previous_is_approved and not created:
        if not instance.user.is_superuser:
            Message.objects.create(
                user=instance.user,
                content=f"آگهی شما با عنوان «{instance.title}» تایید شد!"
            )
        else:
            Message.objects.create(user=instance.user,
                                content=f"شما آکهی «{instance.title}» را تایید کردید!"
            )


def mark_messages_as_read(request):
    request.user.messages.filter(is_read=False).update(is_read=True)
    return render(request, 'cms/messages.html', {'messages': request.user.messages.all()})


def property_create(request):
    if request.method == 'POST':
        property_form = PropertyForm(request.POST, user=request.user)
        images = request.FILES.getlist('images')
        if property_form.is_valid():
            property_obj = property_form.save(commit=False)
            property_obj.user = request.user
            property_obj.save()

            for image in images:
                Image.objects.create(property=property_obj, image=image)

            return redirect('/account/posts')
    else:
        property_form = PropertyForm(user=request.user)

    return render(request, 'cms/property_form.html', {'property_form': property_form})


def property_update(request, pk):
    property_instance = get_object_or_404(Property, pk=pk)
    if request.method == 'POST':
        property_form = PropertyForm(request.POST, instance=property_instance)
        if property_form.is_valid():
            if not request.user.is_superuser:
                property_instance = property_form.save(commit=False)
                property_instance.is_approved = False  # Set approval to False
                property_instance.save()
            else:
                property_instance = property_form.save()
            for file in request.FILES.getlist('image'):
                Image.objects.create(property=property_instance, image=file)
            return redirect('/account/posts', pk=property_instance.pk)
    else:
        property_form = PropertyForm(instance=property_instance)

    return render(request, 'cms/property_form.html', {
        'property_form': property_form,
        'property': property_instance,
    })