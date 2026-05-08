from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Story, Review


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    model = User

    list_display = (
        'email',
        'email_verified',
        'is_admin_owner',
        'is_staff',
        'is_active',
    )

    search_fields = ('email',)
    ordering = ('email',)

    fieldsets = UserAdmin.fieldsets + (
        ('Дополнительно', {
            'fields': ('email_verified', 'is_admin_owner')
        }),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )


@admin.register(Story)
class StoryAdmin(admin.ModelAdmin):
    list_display = ('fio', 'story_date', 'author', 'status', 'created_at')
    list_filter = ('status', 'story_date')
    search_fields = ('fio', 'text', 'author__email')
    actions = ['publish_selected']

    @admin.action(description='Опубликовать выбранные истории')
    def publish_selected(self, request, queryset):
        queryset.update(status=Story.STATUS_PUBLISHED)

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('story', 'sender', 'recipient', 'created_at')
    search_fields = ('text', 'sender__email', 'recipient__email', 'story__fio')
    list_filter = ('created_at',)