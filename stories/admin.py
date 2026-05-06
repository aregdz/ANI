from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Story


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ('phone', 'is_admin_owner', 'is_staff', 'is_active')
    search_fields = ('phone',)
    ordering = ('phone',)
    fieldsets = UserAdmin.fieldsets + ((None, {'fields': ('phone', 'is_admin_owner')}),)
    add_fieldsets = ((None, {'classes': ('wide',), 'fields': ('phone', 'password1', 'password2')}),)


@admin.register(Story)
class StoryAdmin(admin.ModelAdmin):
    list_display = ('fio', 'story_date', 'author', 'status', 'created_at')
    list_filter = ('status', 'story_date')
    search_fields = ('fio', 'text', 'author__phone')
    actions = ['publish_selected']

    @admin.action(description='Опубликовать выбранные истории')
    def publish_selected(self, request, queryset):
        queryset.update(status=Story.STATUS_PUBLISHED)
