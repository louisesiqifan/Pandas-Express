from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('detail', views.get_detail, name='detail')
]
