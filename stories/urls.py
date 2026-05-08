from django.contrib.auth import views as auth_views
from django.urls import path
from . import views


urlpatterns = [
    path('', views.home, name='home'),

    path('register/', views.register_view, name='register'),
    path('verify-email/<uidb64>/<token>/', views.verify_email, name='verify_email'),

    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    path(
        'password-reset/',
        auth_views.PasswordResetView.as_view(
            template_name='stories/password_reset.html',
            email_template_name='stories/password_reset_email.html',
            subject_template_name='stories/password_reset_subject.txt',
            success_url='/password-reset/done/',
        ),
        name='password_reset',
    ),

    path(
        'password-reset/done/',
        auth_views.PasswordResetDoneView.as_view(
            template_name='stories/password_reset_done.html',
        ),
        name='password_reset_done',
    ),

    path(
        'reset/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(
            template_name='stories/password_reset_confirm.html',
            success_url='/reset/done/',
        ),
        name='password_reset_confirm',
    ),

    path(
        'reset/done/',
        auth_views.PasswordResetCompleteView.as_view(
            template_name='stories/password_reset_complete.html',
        ),
        name='password_reset_complete',
    ),

    path('stories/add/', views.story_create, name='story_create'),
    path('stories/my/', views.my_stories, name='my_stories'),
    path('stories/<int:pk>/', views.story_detail, name='story_detail'),

    path('admin-panel/', views.admin_panel, name='admin_panel'),
    path('admin-panel/stories/<int:pk>/edit/', views.admin_story_edit, name='admin_story_edit'),
    path('admin-panel/stories/<int:pk>/publish/', views.admin_story_publish, name='admin_story_publish'),
    path('admin-panel/stories/<int:pk>/delete/', views.admin_story_delete, name='admin_story_delete'),
    path('admin-panel/users/<int:pk>/delete/', views.admin_user_delete, name='admin_user_delete'),
    path('admin-panel/users/<int:pk>/stories/', views.admin_user_stories, name='admin_user_stories'),
path('admin-panel/stories/<int:pk>/reviews/', views.admin_story_reviews, name='admin_story_reviews'),
path('admin-panel/reviews/<int:pk>/delete/', views.admin_review_delete, name='admin_review_delete'),
]