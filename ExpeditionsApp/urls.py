from django.urls import path
from .views import *

urlpatterns = [
    path('home/', home, name='home'),
    path('welcome/<str:name>/', welcome, name='ahmed'),
    path('list/', list_expeditions, name='list'),
    path('expedition/<int:pk>/', expedition_detail, name='expedition_detail'),
    path('expedition/<int:pk>/delete/', expedition_delete, name='expedition_delete'),
    path('expedition_list/', Expedition_list.as_view(), name='expedition_list'),
]
