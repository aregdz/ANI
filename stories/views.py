from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render
from .forms import PhoneLoginForm, PhoneRegisterForm, StoryForm
from .models import Story, User


def is_owner_admin(user):
    return user.is_authenticated and user.is_admin_owner


def admin_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not is_owner_admin(request.user):
            raise PermissionDenied('Доступ только для администратора')
        return view_func(request, *args, **kwargs)
    return wrapper


def home(request):
    stories = Story.objects.filter(status=Story.STATUS_PUBLISHED)
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    if date_from:
        stories = stories.filter(story_date__gte=date_from)
    if date_to:
        stories = stories.filter(story_date__lte=date_to)

    story_list = list(stories)
    for story in story_list:
        story.map_x = max(2, min(98, ((float(story.longitude) + 180) / 360) * 100))
        story.map_y = max(6, min(94, ((90 - float(story.latitude)) / 180) * 100))

    return render(request, 'stories/home.html', {
        'stories': story_list,
        'date_from': date_from or '',
        'date_to': date_to or '',
    })


def register_view(request):
    if request.method == 'POST':
        form = PhoneRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Регистрация выполнена')
            return redirect('my_stories')
    else:
        form = PhoneRegisterForm()
    return render(request, 'stories/auth.html', {'form': form, 'title': 'Регистрация'})


def login_view(request):
    if request.method == 'POST':
        form = PhoneLoginForm(request.POST)
        if form.is_valid():
            login(request, form.cleaned_data['user'])
            return redirect('admin_panel' if form.cleaned_data['user'].is_admin_owner else 'my_stories')
    else:
        form = PhoneLoginForm()
    return render(request, 'stories/auth.html', {'form': form, 'title': 'Вход'})


def logout_view(request):
    logout(request)
    return redirect('home')


@login_required
def story_create(request):
    if request.method == 'POST':
        form = StoryForm(request.POST, request.FILES)
        if form.is_valid():
            story = form.save(commit=False)
            story.author = request.user
            story.status = Story.STATUS_PUBLISHED if request.user.is_admin_owner else Story.STATUS_PENDING
            story.save()
            messages.success(request, 'История отправлена на подтверждение' if not request.user.is_admin_owner else 'История опубликована')
            return redirect('my_stories')
    else:
        form = StoryForm()
    return render(request, 'stories/story_form.html', {'form': form, 'title': 'Добавить историю'})


@login_required
def my_stories(request):
    stories = Story.objects.filter(author=request.user)
    return render(request, 'stories/my_stories.html', {'stories': stories})


def story_detail(request, pk):
    story = get_object_or_404(Story, pk=pk)
    if story.status != Story.STATUS_PUBLISHED and not (request.user.is_authenticated and (request.user == story.author or request.user.is_admin_owner)):
        raise PermissionDenied('История еще не опубликована')
    return render(request, 'stories/story_detail.html', {'story': story})


@admin_required
def admin_panel(request):
    stories = Story.objects.select_related('author').all()
    users = User.objects.all().order_by('-is_admin_owner', 'phone')
    return render(request, 'stories/admin_panel.html', {
        'pending_stories': stories.filter(status=Story.STATUS_PENDING),
        'all_stories': stories,
        'users': users,
    })


@admin_required
def admin_story_publish(request, pk):
    story = get_object_or_404(Story, pk=pk)
    story.status = Story.STATUS_PUBLISHED
    story.save(update_fields=['status', 'updated_at'])
    messages.success(request, 'История опубликована')
    return redirect('admin_panel')


@admin_required
def admin_story_edit(request, pk):
    story = get_object_or_404(Story, pk=pk)
    if request.method == 'POST':
        form = StoryForm(request.POST, request.FILES, instance=story)
        if form.is_valid():
            form.save()
            messages.success(request, 'История обновлена')
            return redirect('admin_panel')
    else:
        form = StoryForm(instance=story)
    return render(request, 'stories/story_form.html', {'form': form, 'title': 'Редактировать историю'})


@admin_required
def admin_story_delete(request, pk):
    story = get_object_or_404(Story, pk=pk)
    story.delete()
    messages.success(request, 'История удалена')
    return redirect('admin_panel')


@admin_required
def admin_user_delete(request, pk):
    user = get_object_or_404(User, pk=pk)
    if user.is_admin_owner:
        messages.error(request, 'Нельзя удалить главного администратора')
    else:
        user.delete()
        messages.success(request, 'Пользователь удален')
    return redirect('admin_panel')
