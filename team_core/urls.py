from django.urls import path
from . import views
from .views import dashboard_view, global_search_view, mark_notifications_read

urlpatterns = [
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('search/', global_search_view, name='global_search'),
    path('notifications/', mark_notifications_read, name='notifications'),
]