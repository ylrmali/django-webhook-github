from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('git/', views.git, name='git'),
]

