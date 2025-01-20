from django.urls import path
from . import views


app_name = 'properties'
urlpatterns = [
    path('', views.index_view, name='index'),  
    path('properties/', views.properties_view, name='properties'),  
    path('properties/<slug:slug>', views.property_single_view, name='proprty_single'),  

    # other pages    about, contact
    path('about/', views.AboutView.as_view(), name='about'),  
    path('contact/', views.ContactCreate.as_view(), name='contact'),  
]
