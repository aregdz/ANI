import shutil
import tempfile

from django.contrib.auth.tokens import default_token_generator
from django.core import mail
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from .forms import EmailLoginForm, EmailRegisterForm, ReviewForm, StoryForm
from .models import Review, Story, StoryMedia, User


TEST_MEDIA_ROOT = tempfile.mkdtemp()
TEST_SETTINGS = override_settings(
    EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
    MEDIA_ROOT=TEST_MEDIA_ROOT,
    STATICFILES_STORAGE='django.contrib.staticfiles.storage.StaticFilesStorage',
    STORAGES={
        'default': {
            'BACKEND': 'django.core.files.storage.FileSystemStorage',
        },
        'staticfiles': {
            'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage',
        },
    },
)


def tearDownModule():
    shutil.rmtree(TEST_MEDIA_ROOT, ignore_errors=True)


def create_user(email='user@example.com', password='StrongPass123', **extra):
    extra.setdefault('email_verified', True)
    return User.objects.create_user(
        email=email,
        password=password,
        **extra
    )


def story_data(**extra):
    data = {
        'fio': 'Test Hero',
        'story_date': '2024-01-10',
        'latitude': '55.755800',
        'longitude': '37.617300',
        'text': 'Story text for testing.',
    }
    data.update(extra)
    return data


def create_story(author=None, **extra):
    if author is None:
        author = create_user()

    data = story_data()
    data.update({
        'author': author,
        'status': Story.STATUS_PUBLISHED,
    })
    data.update(extra)
    return Story.objects.create(**data)


@TEST_SETTINGS
class ModelTests(TestCase):
    def test_create_user_sets_email_and_username(self):
        user = User.objects.create_user(
            email='User@Example.COM',
            password='StrongPass123'
        )

        self.assertEqual(user.email, 'User@example.com')
        self.assertEqual(user.username, 'User@example.com')
        self.assertTrue(user.check_password('StrongPass123'))

    def test_create_superuser_is_admin_and_verified(self):
        user = User.objects.create_superuser(
            email='admin@example.com',
            password='StrongPass123'
        )

        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_admin_owner)
        self.assertTrue(user.email_verified)

    def test_story_default_status_is_pending(self):
        user = create_user()
        story = Story.objects.create(
            author=user,
            **story_data()
        )

        self.assertEqual(story.status, Story.STATUS_PENDING)

    def test_review_is_linked_to_story_sender_and_recipient(self):
        author = create_user(email='author@example.com')
        sender = create_user(email='sender@example.com')
        story = create_story(author=author)

        review = Review.objects.create(
            story=story,
            sender=sender,
            recipient=author,
            text='Good story',
            rating=5
        )

        self.assertEqual(review.story, story)
        self.assertEqual(review.sender, sender)
        self.assertEqual(review.recipient, author)


@TEST_SETTINGS
class FormTests(TestCase):
    def test_register_form_rejects_duplicate_email(self):
        create_user(email='duplicate@example.com')

        form = EmailRegisterForm(data={
            'email': 'duplicate@example.com',
            'password1': 'StrongPass123',
            'password2': 'StrongPass123',
        })

        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)

    def test_login_form_accepts_valid_credentials(self):
        user = create_user(
            email='login@example.com',
            password='StrongPass123'
        )

        form = EmailLoginForm(data={
            'email': 'login@example.com',
            'password': 'StrongPass123',
        })

        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['user'], user)

    def test_login_form_rejects_wrong_password(self):
        create_user(
            email='login@example.com',
            password='StrongPass123'
        )

        form = EmailLoginForm(data={
            'email': 'login@example.com',
            'password': 'WrongPass123',
        })

        self.assertFalse(form.is_valid())

    def test_story_form_accepts_required_fields(self):
        form = StoryForm(data=story_data())

        self.assertTrue(form.is_valid())

    def test_review_form_accepts_rating_and_text(self):
        form = ReviewForm(data={
            'rating': 4,
            'text': 'Useful review',
        })

        self.assertTrue(form.is_valid())


@TEST_SETTINGS
class HomeViewTests(TestCase):
    def setUp(self):
        self.user = create_user()
        self.published = create_story(
            author=self.user,
            fio='Published story',
            story_date='2024-01-10',
            status=Story.STATUS_PUBLISHED
        )
        self.pending = create_story(
            author=self.user,
            fio='Pending story',
            story_date='2024-01-15',
            status=Story.STATUS_PENDING
        )

    def test_home_shows_only_published_stories(self):
        response = self.client.get(reverse('home'))

        self.assertEqual(response.status_code, 200)
        self.assertIn(self.published, response.context['stories'])
        self.assertNotIn(self.pending, response.context['stories'])

    def test_home_filters_stories_by_date_range(self):
        old_story = create_story(
            author=self.user,
            fio='Old story',
            story_date='2023-05-01',
            status=Story.STATUS_PUBLISHED
        )

        response = self.client.get(reverse('home'), {
            'date_from': '2024-01-01',
            'date_to': '2024-12-31',
        })

        stories = list(response.context['stories'])
        self.assertIn(self.published, stories)
        self.assertNotIn(old_story, stories)

    def test_home_keeps_filter_values_in_context(self):
        response = self.client.get(reverse('home'), {
            'date_from': '2024-01-01',
            'date_to': '2024-12-31',
        })

        self.assertEqual(response.context['date_from'], '2024-01-01')
        self.assertEqual(response.context['date_to'], '2024-12-31')


@TEST_SETTINGS
class AuthViewTests(TestCase):
    def test_register_creates_unverified_user_and_sends_email(self):
        response = self.client.post(reverse('register'), {
            'email': 'new@example.com',
            'password1': 'StrongPass123',
            'password2': 'StrongPass123',
        })

        user = User.objects.get(email='new@example.com')
        self.assertRedirects(response, reverse('login'))
        self.assertFalse(user.email_verified)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('verify-email', mail.outbox[0].body)

    def test_verified_user_can_login(self):
        create_user(
            email='login@example.com',
            password='StrongPass123',
            email_verified=True
        )

        response = self.client.post(reverse('login'), {
            'email': 'login@example.com',
            'password': 'StrongPass123',
        })

        self.assertRedirects(response, reverse('my_stories'))

    def test_unverified_user_cannot_login(self):
        create_user(
            email='login@example.com',
            password='StrongPass123',
            email_verified=False
        )

        response = self.client.post(reverse('login'), {
            'email': 'login@example.com',
            'password': 'StrongPass123',
        })

        self.assertRedirects(response, reverse('login'))

    def test_admin_user_logs_in_to_admin_panel(self):
        create_user(
            email='admin@example.com',
            password='StrongPass123',
            is_admin_owner=True,
            email_verified=False
        )

        response = self.client.post(reverse('login'), {
            'email': 'admin@example.com',
            'password': 'StrongPass123',
        })

        self.assertRedirects(response, reverse('admin_panel'))

    def test_verify_email_marks_user_as_verified(self):
        user = create_user(
            email='verify@example.com',
            email_verified=False
        )
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)

        response = self.client.get(reverse('verify_email', kwargs={
            'uidb64': uid,
            'token': token,
        }))

        user.refresh_from_db()
        self.assertRedirects(response, reverse('login'))
        self.assertTrue(user.email_verified)

    def test_verify_email_rejects_invalid_token(self):
        user = create_user(
            email='verify@example.com',
            email_verified=False
        )
        uid = urlsafe_base64_encode(force_bytes(user.pk))

        response = self.client.get(reverse('verify_email', kwargs={
            'uidb64': uid,
            'token': 'bad-token',
        }))

        user.refresh_from_db()
        self.assertRedirects(response, reverse('login'))
        self.assertFalse(user.email_verified)


@TEST_SETTINGS
class StoryViewTests(TestCase):
    def setUp(self):
        self.user = create_user(
            email='author@example.com',
            password='StrongPass123'
        )
        self.admin = create_user(
            email='admin@example.com',
            password='StrongPass123',
            is_admin_owner=True
        )

    def test_story_create_requires_login(self):
        response = self.client.get(reverse('story_create'))

        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('login'), response['Location'])

    def test_regular_user_creates_pending_story(self):
        self.client.force_login(self.user)

        response = self.client.post(reverse('story_create'), story_data())

        story = Story.objects.get(author=self.user)
        self.assertRedirects(response, reverse('my_stories'))
        self.assertEqual(story.status, Story.STATUS_PENDING)

    def test_admin_creates_published_story(self):
        self.client.force_login(self.admin)

        response = self.client.post(reverse('story_create'), story_data())

        story = Story.objects.get(author=self.admin)
        self.assertRedirects(response, reverse('my_stories'))
        self.assertEqual(story.status, Story.STATUS_PUBLISHED)

    def test_story_create_saves_uploaded_photo(self):
        self.client.force_login(self.user)
        photo = SimpleUploadedFile(
            'photo.jpg',
            b'test image content',
            content_type='image/jpeg'
        )
        data = story_data()
        data['photos'] = photo

        response = self.client.post(reverse('story_create'), data)

        story = Story.objects.get(author=self.user)
        self.assertRedirects(response, reverse('my_stories'))
        self.assertEqual(story.media_files.count(), 1)
        self.assertEqual(
            story.media_files.first().media_type,
            StoryMedia.MEDIA_PHOTO
        )

    def test_my_stories_shows_only_current_user_stories(self):
        other = create_user(email='other@example.com')
        own_story = create_story(
            author=self.user,
            fio='Own story',
            status=Story.STATUS_PENDING
        )
        create_story(
            author=other,
            fio='Other story',
            status=Story.STATUS_PENDING
        )
        self.client.force_login(self.user)

        response = self.client.get(reverse('my_stories'))

        self.assertEqual(response.status_code, 200)
        self.assertIn(own_story, response.context['stories'])
        self.assertEqual(list(response.context['stories']), [own_story])


@TEST_SETTINGS
class StoryDetailAndReviewTests(TestCase):
    def setUp(self):
        self.author = create_user(
            email='author@example.com',
            password='StrongPass123'
        )
        self.reader = create_user(
            email='reader@example.com',
            password='StrongPass123'
        )
        self.admin = create_user(
            email='admin@example.com',
            password='StrongPass123',
            is_admin_owner=True
        )
        self.published_story = create_story(
            author=self.author,
            status=Story.STATUS_PUBLISHED
        )
        self.pending_story = create_story(
            author=self.author,
            status=Story.STATUS_PENDING
        )

    def test_published_story_is_visible_to_anonymous_user(self):
        response = self.client.get(reverse('story_detail', kwargs={
            'pk': self.published_story.pk,
        }))

        self.assertEqual(response.status_code, 200)

    def test_pending_story_is_hidden_from_anonymous_user(self):
        response = self.client.get(reverse('story_detail', kwargs={
            'pk': self.pending_story.pk,
        }))

        self.assertEqual(response.status_code, 403)

    def test_pending_story_is_visible_to_author(self):
        self.client.force_login(self.author)

        response = self.client.get(reverse('story_detail', kwargs={
            'pk': self.pending_story.pk,
        }))

        self.assertEqual(response.status_code, 200)

    def test_pending_story_is_visible_to_admin(self):
        self.client.force_login(self.admin)

        response = self.client.get(reverse('story_detail', kwargs={
            'pk': self.pending_story.pk,
        }))

        self.assertEqual(response.status_code, 200)

    def test_anonymous_user_cannot_create_review(self):
        response = self.client.post(reverse('story_detail', kwargs={
            'pk': self.published_story.pk,
        }), {
            'rating': 5,
            'text': 'Anonymous review',
        })

        self.assertRedirects(response, reverse('login'))
        self.assertEqual(Review.objects.count(), 0)

    def test_authenticated_user_can_create_review(self):
        self.client.force_login(self.reader)

        response = self.client.post(reverse('story_detail', kwargs={
            'pk': self.published_story.pk,
        }), {
            'rating': 5,
            'text': 'Good story',
        })

        review = Review.objects.get()
        self.assertRedirects(response, reverse(
            'story_detail',
            kwargs={'pk': self.published_story.pk}
        ))
        self.assertEqual(review.story, self.published_story)
        self.assertEqual(review.sender, self.reader)
        self.assertEqual(review.recipient, self.author)


@TEST_SETTINGS
class AdminViewTests(TestCase):
    def setUp(self):
        self.user = create_user(
            email='user@example.com',
            password='StrongPass123'
        )
        self.admin = create_user(
            email='admin@example.com',
            password='StrongPass123',
            is_admin_owner=True
        )
        self.story = create_story(
            author=self.user,
            status=Story.STATUS_PENDING
        )

    def test_admin_panel_denies_regular_user(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse('admin_panel'))

        self.assertEqual(response.status_code, 403)

    def test_admin_panel_allows_admin_user(self):
        self.client.force_login(self.admin)

        response = self.client.get(reverse('admin_panel'))

        self.assertEqual(response.status_code, 200)
        self.assertIn(self.story, response.context['pending_stories'])

    def test_admin_can_publish_story(self):
        self.client.force_login(self.admin)

        response = self.client.get(reverse('admin_story_publish', kwargs={
            'pk': self.story.pk,
        }))

        self.story.refresh_from_db()
        self.assertRedirects(response, reverse('admin_panel'))
        self.assertEqual(self.story.status, Story.STATUS_PUBLISHED)

    def test_admin_can_delete_story(self):
        self.client.force_login(self.admin)

        response = self.client.get(reverse('admin_story_delete', kwargs={
            'pk': self.story.pk,
        }))

        self.assertRedirects(response, reverse('admin_panel'))
        self.assertFalse(Story.objects.filter(pk=self.story.pk).exists())

    def test_admin_can_delete_regular_user(self):
        self.client.force_login(self.admin)

        response = self.client.get(reverse('admin_user_delete', kwargs={
            'pk': self.user.pk,
        }))

        self.assertRedirects(response, reverse('admin_panel'))
        self.assertFalse(User.objects.filter(pk=self.user.pk).exists())

    def test_admin_cannot_delete_main_admin_user(self):
        self.client.force_login(self.admin)

        response = self.client.get(reverse('admin_user_delete', kwargs={
            'pk': self.admin.pk,
        }))

        self.assertRedirects(response, reverse('admin_panel'))
        self.assertTrue(User.objects.filter(pk=self.admin.pk).exists())

    def test_admin_can_delete_review(self):
        review = Review.objects.create(
            story=self.story,
            sender=self.user,
            recipient=self.admin,
            text='Review for deletion',
            rating=3
        )
        self.client.force_login(self.admin)

        response = self.client.get(reverse('admin_review_delete', kwargs={
            'pk': review.pk,
        }))

        self.assertRedirects(response, reverse(
            'admin_story_reviews',
            kwargs={'pk': self.story.pk}
        ))
        self.assertFalse(Review.objects.filter(pk=review.pk).exists())
