from http import HTTPStatus

from django.test import Client, TestCase
from django.urls import reverse
from pytils.translit import slugify

from notes.forms import WARNING
from notes.models import Note, User


class TestNoteCreation(TestCase):
    NOTE_TITLE = 'Nice Title'
    NOTE_TEXT = 'Pro100 Text'
    NOTE_SLUG = 'test_slug'

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(username='IamGroot')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.user)
        cls.form_data = {
            'title': cls.NOTE_TITLE,
            'text': cls.NOTE_TEXT,
            'slug': cls.NOTE_SLUG,
        }

    def test_anonymous_user_cant_create_note(self):
        self.client.post(reverse('notes:add'), data=self.form_data)
        self.assertRedirects(
            self.client.post(reverse('notes:add'), data=self.form_data),
            f'{reverse("users:login")}?next={reverse("notes:add")}'
        )
        self.assertEqual(Note.objects.count(), 0)

    def test_user_can_create_note(self):
        self.assertRedirects(
            self.auth_client.post(reverse('notes:add'), data=self.form_data),
            reverse('notes:success')
        )
        self.assertEqual(Note.objects.count(), 1)
        note = Note.objects.get()
        self.assertEqual(note.title, self.NOTE_TITLE)
        self.assertEqual(note.text, self.NOTE_TEXT)
        self.assertEqual(note.slug, self.NOTE_SLUG)
        self.assertEqual(note.author, self.user)


class TestNoteEditDeleteUseNotUniqueSlug(TestCase):
    NOTE_TITLE = 'Nice Title'
    NOTE_TEXT = 'Pro100 Text'
    NOTE_SLUG = 'test_slug'
    NEW_NOTE_TITLE = 'New Title'
    NEW_NOTE_TEXT = 'New Text'
    NEW_NOTE_SLUG = 'new_slug'

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='IceFrog')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.reader = User.objects.create(username='IamGroot')
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        cls.note = Note.objects.create(
            title=cls.NOTE_TITLE,
            text=cls.NOTE_TEXT,
            author=cls.author,
            slug=cls.NOTE_SLUG,
        )
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))
        cls.success_url = reverse('notes:success')
        cls.form_data = {
            'title': cls.NEW_NOTE_TITLE,
            'text': cls.NEW_NOTE_TEXT,
            'slug': cls.NEW_NOTE_SLUG,
        }

    def test_user_cant_use_not_unique_slug(self):
        self.assertFormError(
            self.author_client.post(
                reverse('notes:add'),
                data={
                    'title': self.NEW_NOTE_TITLE,
                    'text': self.NEW_NOTE_TEXT,
                    'slug': self.NOTE_SLUG,
                }
            ),
            form='form',
            field='slug',
            errors=self.NOTE_SLUG + WARNING
        )
        self.assertEqual(Note.objects.count(), 1)

    def test_empty_slug(self):
        url = reverse('notes:add')
        response = self.author_client.post(url, data={
            'title': self.NEW_NOTE_TITLE,
            'text': self.NEW_NOTE_TEXT,
        })
        self.assertRedirects(response, self.success_url)
        self.assertEqual(Note.objects.count(), 2)
        note = Note.objects.get(slug=slugify(self.NEW_NOTE_TITLE))
        expected_slug = slugify(self.NEW_NOTE_TITLE)
        self.assertEqual(note.slug, expected_slug)

    def test_author_can_delete_note(self):
        self.assertRedirects(
            self.author_client.delete(self.delete_url),
            self.success_url
        )
        self.assertEqual(Note.objects.count(), 0)

    def test_user_cant_delete_comment_of_another_user(self):
        self.assertEqual(
            self.reader_client.delete(self.delete_url).status_code,
            HTTPStatus.NOT_FOUND
        )
        self.assertEqual(Note.objects.count(), 1)

    def test_author_can_edit_comment(self):
        self.assertRedirects(
            self.author_client.post(self.edit_url, data=self.form_data),
            self.success_url
        )
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, self.NEW_NOTE_TITLE)
        self.assertEqual(self.note.text, self.NEW_NOTE_TEXT)
        self.assertEqual(self.note.slug, self.NEW_NOTE_SLUG)

    def test_user_cant_edit_comment_of_another_user(self):
        self.assertEqual(
            self.reader_client.post(
                self.edit_url, data=self.form_data
            ).status_code,
            HTTPStatus.NOT_FOUND
        )
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, self.NOTE_TITLE)
        self.assertEqual(self.note.text, self.NOTE_TEXT)
        self.assertEqual(self.note.slug, self.NOTE_SLUG)
