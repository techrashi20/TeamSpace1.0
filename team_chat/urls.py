from django.urls import path
from . import views

urlpatterns = [
    path('', views.chat_room_view, {'room_name': 'general'}, name='chat_main'),
    path('<str:room_name>/', views.chat_room_view, name='chat_room'),
]