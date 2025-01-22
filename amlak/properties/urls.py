from django.urls import path
from django.contrib.auth import views

from .views import index_view, properties_view, property_single_view, AboutView, ContactCreate, UserCreate, dashboard_view, mark_messages_as_read


app_name = 'properties'
urlpatterns = [
    path('', index_view, name='index'),  
    path('properties/', properties_view, name='properties'),  
    path('properties/<slug:slug>', property_single_view, name='proprty_single'),  

    # other pages    about, contact
    path('about/', AboutView.as_view(), name='about'),  
    path('contact/', ContactCreate.as_view(), name='contact'),  

    # cms
    path('account/', dashboard_view, name='account'),  
    path('messages/', mark_messages_as_read, name='messages'),  

]

# login urls
urlpatterns += [
    path("login/", views.LoginView.as_view(), name="login"),
    path("register/", UserCreate.as_view(), name="register"),

]
