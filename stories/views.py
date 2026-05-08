from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.urls import reverse
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode

from .forms import (
    EmailLoginForm,
    EmailRegisterForm,
    StoryForm,
    ReviewForm
)

from .models import (
    Story,
    User,
    Review,
    StoryMedia
)


def is_owner_admin(user):
    return user.is_authenticated and user.is_admin_owner


def admin_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not is_owner_admin(request.user):
            raise PermissionDenied('Доступ только для администратора')

        return view_func(request, *args, **kwargs)

    return wrapper


def home(request):
    stories = Story.objects.filter(
        status=Story.STATUS_PUBLISHED
    )

    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')

    if date_from:
        stories = stories.filter(
            story_date__gte=date_from
        )

    if date_to:
        stories = stories.filter(
            story_date__lte=date_to
        )

    return render(request, 'stories/home.html', {
        'stories': stories,
        'date_from': date_from or '',
        'date_to': date_to or '',
    })


def register_view(request):
    if request.method == 'POST':
        form = EmailRegisterForm(request.POST)

        if form.is_valid():
            user = form.save(commit=False)
            user.email = form.cleaned_data['email'].lower()
            user.username = user.email
            user.email_verified = False
            user.save()

            send_verification_email(request, user)

            messages.success(
                request,
                'Регистрация выполнена. Мы отправили письмо для подтверждения email.'
            )

            return redirect('login')

    else:
        form = EmailRegisterForm()

    return render(request, 'stories/auth.html', {
        'form': form,
        'title': 'Регистрация',
        'hint': 'Введите email и пароль. После регистрации подтвердите email по ссылке из письма.'
    })


def login_view(request):
    if request.method == 'POST':
        form = EmailLoginForm(request.POST)

        if form.is_valid():
            login(
                request,
                form.cleaned_data['user']
            )

            if form.cleaned_data['user'].is_admin_owner:
                return redirect('admin_panel')

            return redirect('my_stories')

    else:
        form = EmailLoginForm()

    return render(request, 'stories/auth.html', {
    'form': form,
    'title': 'Вход',
    'hint': 'Войдите по email и паролю.',
    'show_forgot_password': True,
})


def logout_view(request):
    logout(request)
    return redirect('home')


@login_required
def story_create(request):
    if request.method == 'POST':
        form = StoryForm(
            request.POST,
            request.FILES
        )

        if form.is_valid():
            story = form.save(commit=False)

            story.author = request.user

            if request.user.is_admin_owner:
                story.status = Story.STATUS_PUBLISHED
            else:
                story.status = Story.STATUS_PENDING

            story.save()

            # ===== Фото =====
            photos = request.FILES.getlist('photos')

            if not photos and request.FILES.get('photos'):
                photos = [request.FILES.get('photos')]

            for file in photos:
                StoryMedia.objects.create(
                    story=story,
                    media_type=StoryMedia.MEDIA_PHOTO,
                    file=file
                )

            # ===== Видео =====
            videos = request.FILES.getlist('videos')

            if not videos and request.FILES.get('videos'):
                videos = [request.FILES.get('videos')]

            for file in videos:
                StoryMedia.objects.create(
                    story=story,
                    media_type=StoryMedia.MEDIA_VIDEO,
                    file=file
                )

            # ===== Аудио =====
            audios = request.FILES.getlist('audios')

            if not audios and request.FILES.get('audios'):
                audios = [request.FILES.get('audios')]

            for file in audios:
                StoryMedia.objects.create(
                    story=story,
                    media_type=StoryMedia.MEDIA_AUDIO,
                    file=file
                )
            if request.user.is_admin_owner:
                messages.success(
                    request,
                    'История опубликована'
                )
            else:
                messages.success(
                    request,
                    'История отправлена на подтверждение'
                )

            return redirect('my_stories')

    else:
        form = StoryForm()

    return render(request, 'stories/story_form.html', {
        'form': form,
        'title': 'Добавить историю'
    })


@login_required
def my_stories(request):
    stories = Story.objects.filter(
        author=request.user
    )

    return render(request, 'stories/my_stories.html', {
        'stories': stories
    })


def story_detail(request, pk):
    story = get_object_or_404(
        Story,
        pk=pk
    )

    if story.status != Story.STATUS_PUBLISHED:
        allowed = (
            request.user.is_authenticated
            and (
                request.user == story.author
                or request.user.is_admin_owner
            )
        )

        if not allowed:
            raise PermissionDenied(
                'История еще не опубликована'
            )

    reviews = story.reviews.select_related(
        'sender',
        'recipient'
    )

    if request.method == 'POST':
        if not request.user.is_authenticated:
            messages.error(
                request,
                'Чтобы оставить отзыв, нужно войти.'
            )

            return redirect('login')

        form = ReviewForm(request.POST)

        if form.is_valid():
            review = form.save(commit=False)

            review.story = story
            review.sender = request.user
            review.recipient = story.author

            review.save()

            messages.success(
                request,
                'Отзыв добавлен.'
            )

            return redirect(
                'story_detail',
                pk=story.pk
            )

    else:
        form = ReviewForm()

    return render(request, 'stories/story_detail.html', {
        'story': story,
        'reviews': reviews,
        'review_form': form,
    })


@admin_required
def admin_panel(request):
    stories = Story.objects.select_related(
        'author'
    ).all()

    users = User.objects.all().order_by(
        '-is_admin_owner',
        'email'
    )

    return render(request, 'stories/admin_panel.html', {
        'pending_stories': stories.filter(
            status=Story.STATUS_PENDING
        ),

        'all_stories': stories,
        'users': users,
    })


@admin_required
def admin_story_publish(request, pk):
    story = get_object_or_404(
        Story,
        pk=pk
    )

    story.status = Story.STATUS_PUBLISHED

    story.save(update_fields=[
        'status',
        'updated_at'
    ])

    messages.success(
        request,
        'История опубликована'
    )

    return redirect('admin_panel')


@admin_required
def admin_story_edit(request, pk):
    story = get_object_or_404(
        Story,
        pk=pk
    )

    if request.method == 'POST':
        form = StoryForm(
            request.POST,
            request.FILES,
            instance=story
        )

        if form.is_valid():
            form.save()

            messages.success(
                request,
                'История обновлена'
            )

            return redirect('admin_panel')

    else:
        form = StoryForm(instance=story)

    return render(request, 'stories/story_form.html', {
        'form': form,
        'title': 'Редактировать историю'
    })


@admin_required
def admin_story_delete(request, pk):
    story = get_object_or_404(
        Story,
        pk=pk
    )

    story.delete()

    messages.success(
        request,
        'История удалена'
    )

    return redirect('admin_panel')


@admin_required
def admin_user_delete(request, pk):
    user = get_object_or_404(
        User,
        pk=pk
    )

    if user.is_admin_owner:
        messages.error(
            request,
            'Нельзя удалить главного администратора'
        )

    else:
        user.delete()

        messages.success(
            request,
            'Пользователь удален'
        )

    return redirect('admin_panel')


@admin_required
def admin_user_stories(request, pk):
    user_obj = get_object_or_404(
        User,
        pk=pk
    )

    stories = Story.objects.filter(
        author=user_obj
    ).order_by('-created_at')

    return render(
        request,
        'stories/admin_user_stories.html',
        {
            'user_obj': user_obj,
            'stories': stories,
        }
    )


@admin_required
def admin_story_reviews(request, pk):
    story = get_object_or_404(
        Story,
        pk=pk
    )

    reviews = story.reviews.select_related(
        'sender',
        'recipient'
    ).all()

    return render(
        request,
        'stories/admin_story_reviews.html',
        {
            'story': story,
            'reviews': reviews,
        }
    )


@admin_required
def admin_review_delete(request, pk):
    review = get_object_or_404(
        Review,
        pk=pk
    )

    story_id = review.story.id

    review.delete()

    messages.success(
        request,
        'Отзыв удалён'
    )

    return redirect(
        'admin_story_reviews',
        pk=story_id
    )

def send_verification_email(request, user):
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)

    verify_url = request.build_absolute_uri(
        reverse('verify_email', kwargs={
            'uidb64': uid,
            'token': token,
        })
    )

    send_mail(
        'Подтверждение email А.Н.И',
        (
            'Здравствуйте!\n\n'
            'Для завершения регистрации подтвердите ваш email:\n\n'
            f'{verify_url}\n\n'
            'Если вы не регистрировались на сайте А.Н.И, просто проигнорируйте это письмо.'
        ),
        None,
        [user.email],
        fail_silently=False,
    )


def verify_email(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except Exception:
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.email_verified = True
        user.save(update_fields=['email_verified'])

        messages.success(request, 'Email успешно подтверждён. Теперь можно войти.')
        return redirect('login')

    messages.error(request, 'Ссылка подтверждения недействительна или устарела.')
    return redirect('login')