from django.urls import path
from . import views

urlpatterns = [
    path('', views.notifications_list_view, name='notifications_list'),
    path('api/count/', views.notifications_count_api, name='notifications_count_api'),
    path('read/<int:pk>/', views.mark_notification_read, name='mark_notification_read'),
]
