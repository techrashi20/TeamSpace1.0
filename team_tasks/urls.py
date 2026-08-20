from django.urls import path
from . import views

urlpatterns = [
    path('board/', views.task_board_view, name='task_board'),
    path('list/', views.task_list_view, name='task_list'),
    path('create/', views.create_task_view, name='create_task'),
    path('detail/<int:pk>/', views.task_detail_view, name='task_detail'),
    path('<int:pk>/update-status/', views.update_task_status, name='update_task_status'),
    path('api/update-status/', views.update_task_status_api, name='update_task_status_api'),
    path('convert-mail/<int:mail_id>/', views.convert_mail_to_task, name='convert_mail_to_task'),
    path('calendar/', views.calendar_view, name='task_calendar'),
]