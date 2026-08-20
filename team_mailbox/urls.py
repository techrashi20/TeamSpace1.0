from django.urls import path
from . import views

urlpatterns = [
    path('inbox/', views.inbox_view, name='inbox'),
    path('sent/', views.sent_view, name='sent'),
    path('compose/', views.compose_view, name='compose'),
    path('compose/draft/<int:draft_id>/', views.compose_view, name='edit_draft'),
    path('drafts/', views.drafts_view, name='drafts'),
    path('archive/', views.archive_view, name='archive'),
    path('archive/toggle/<int:pk>/', views.toggle_archive_view, name='toggle_archive'),
    path('delete/<int:pk>/', views.delete_message_view, name='delete_message'),
    path('<int:pk>/', views.mail_detail_view, name='message_detail'),
]