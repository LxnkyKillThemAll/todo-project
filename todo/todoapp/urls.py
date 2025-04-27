from django.urls import path
from . import views

urlpatterns = [
    path('', views.task_list, name='task_list'),
    path('task/create/', views.task_create, name='task_create'),
    path('task/<int:pk>/edit/', views.task_update, name='task_update'),
    path('task/<int:pk>/delete/', views.task_delete, name='task_delete'),
    path('archived/', views.archived_tasks, name='archived_tasks'),

    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
]
