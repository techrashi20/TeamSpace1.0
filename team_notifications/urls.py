from django.urls import path
from . import views

urlpatterns = [
    path('', views.notifications_list_view, name='notifications_list'),
    path('read/<int:pk>/', views.mark_notification_read, name='mark_notification_read'),
    path('api/mark-all-read/', views.mark_all_read_api, name='mark_all_read_api'),
]