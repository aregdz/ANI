from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('stories/add/', views.story_create, name='story_create'),
    path('stories/my/', views.my_stories, name='my_stories'),
    path('stories/<int:pk>/', views.story_detail, name='story_detail'),
    path('admin-panel/', views.admin_panel, name='admin_panel'),
    path('admin-panel/stories/<int:pk>/edit/', views.admin_story_edit, name='admin_story_edit'),
    path('admin-panel/stories/<int:pk>/publish/', views.admin_story_publish, name='admin_story_publish'),
    path('admin-panel/stories/<int:pk>/delete/', views.admin_story_delete, name='admin_story_delete'),
    path('admin-panel/users/<int:pk>/delete/', views.admin_user_delete, name='admin_user_delete'),
]
