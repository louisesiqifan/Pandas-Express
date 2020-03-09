from django.urls import path

from . import views

urlpatterns = [
    path('', views.search, name='home'),
    path('advance', views.advance, name='advance'),
    path('detail', views.get_detail, name='detail'),
]
