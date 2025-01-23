from django.urls import path
from django.contrib.auth import views

from django.contrib.auth import views as auth_views

from .views import index_view, properties_view, property_single_view,\
    AboutView,ContactCreate, UserCreate, UpdateUser, mark_messages_as_read,\
    PostsView, CreateProperty, UpdateProperty


app_name = 'properties'
urlpatterns = [
    path('', index_view, name='index'),  
    path('properties/', properties_view, name='properties'),  
    path('properties/<int:pk>', property_single_view, name='proprty_single'),  

    # other pages    about, contact
    path('about/', AboutView.as_view(), name='about'),
    path('contact/', ContactCreate.as_view(), name='contact'),

    # cms
    path('account/', UpdateUser.as_view(), name='account'),  
    path('account/messages/', mark_messages_as_read, name='messages'),
    path('account/posts/', PostsView.as_view(), name='posts'),
    path('account/posts/create', CreateProperty.as_view(), name='create'),
    path('account/posts/<int:pk>/update', UpdateProperty.as_view(), name='update'),

]

# login urls
urlpatterns += [
    path("login/", views.LoginView.as_view(), name="login"),
    path("register/", UserCreate.as_view(), name="register"),
    path("logout/", views.LogoutView.as_view(), name="logout"),

]
