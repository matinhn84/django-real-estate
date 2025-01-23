from django.shortcuts import render
from django.contrib import messages
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404
from django.db.models import Count
from django.contrib.auth.models import User
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone

from django.views.generic import ListView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Property, Category, Contact, Message
from .mixins import LimitFieldsMixin
# Create your views here.


def index_view(request):
    properties = Property.objects.prefetch_related('images').filter(is_approved=True).order_by('-post_date')[:6]
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

    properties = Property.objects.prefetch_related('images').filter(is_approved=True).order_by('-post_date')

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


def property_single_view(request, pk):
    property = get_object_or_404(Property, pk=pk)
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
    
# register user
class UserCreate(CreateView):
    model = User
    fields = "__all__"
    success_url = reverse_lazy('properties:index')



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
    Message.objects.create(user=instance.user,
                           content=f"شما آکهی «{instance.title}» را تایید کردید!"
            )


def mark_messages_as_read(request):
    request.user.messages.filter(is_read=False).update(is_read=True)
    return render(request, 'cms/messages.html', {'messages': request.user.messages.all()})

class CreateProperty(LimitFieldsMixin, LoginRequiredMixin, CreateView):
    model = Property
    fields = ['title', 'location', 'built_year',\
               'type', 'category', 'status', 'bedroom',\
                  'bathroom', 'description', 'price',\
                      'floors', 'parking', 'lot_area', 'floor_area',\
                          'elevator', 'warehouse', 'user', 'is_approved']
    

    limited_fields = ['title', 'location', 'built_year',\
               'type', 'category', 'status', 'bedroom',\
                  'bathroom', 'description', 'price',\
                      'floors', 'parking', 'lot_area', 'floor_area',\
                          'elevator', 'warehouse']
    template_name = 'cms/property_form.html'


class UpdateProperty(LimitFieldsMixin, UpdateUser):
    model = Property
    success_url = reverse_lazy('properties:posts')
    template_name = 'cms/property_form.html'

    fields = ['title', 'location', 'built_year',\
               'type', 'category', 'status', 'bedroom',\
                  'bathroom', 'description', 'price',\
                      'floors', 'parking', 'lot_area', 'floor_area',\
                          'elevator', 'warehouse', 'user', 'is_approved']
    

    limited_fields = ['title', 'location', 'built_year',\
               'type', 'category', 'status', 'bedroom',\
                  'bathroom', 'description', 'price',\
                      'floors', 'parking', 'lot_area', 'floor_area',\
                          'elevator', 'warehouse']
    
    def get_object(self, queryset=None):
        return get_object_or_404(Property, pk=self.kwargs['pk'], user=self.request.user)