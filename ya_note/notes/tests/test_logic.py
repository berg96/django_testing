from http import HTTPStatus

from django.test import Client, TestCase
from django.urls import reverse
from pytils.translit import slugify

from notes.forms import WARNING
from notes.models import Note, User


NOTE_SLUG_FOR_TEST = 'test_slug'
ADD_URL = reverse('notes:add')
SUCCESS_URL = reverse('notes:success')
EDIT_URL = reverse('notes:edit', args=(NOTE_SLUG_FOR_TEST,))
DELETE_URL = reverse('notes:delete', args=(NOTE_SLUG_FOR_TEST,))
LOGIN_URL = reverse('users:login')


class TestNoteCreation(TestCase):
    NOTE_TITLE = 'Test Title'
    NOTE_TEXT = 'Test Text'

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(username='IamGroot')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.user)
        cls.form_data = {
            'title': cls.NOTE_TITLE,
            'text': cls.NOTE_TEXT,
            'slug': NOTE_SLUG_FOR_TEST,
        }

    def test_anonymous_user_cant_create_note(self):
        count_notes_before_post = Note.objects.count()
        self.client.post(ADD_URL, data=self.form_data)
        self.assertRedirects(
            self.client.post(ADD_URL, data=self.form_data),
            f'{LOGIN_URL}?next={ADD_URL}'
        )
        count_notes_after_post = Note.objects.count()
        self.assertEqual(count_notes_before_post, count_notes_after_post)

    def test_user_can_create_note(self):
        notes_before_post_set = set(Note.objects.all())
        self.assertRedirects(
            self.auth_client.post(ADD_URL, data=self.form_data),
            SUCCESS_URL
        )
        notes_after_post_set = set(Note.objects.all())
        created_note = (notes_after_post_set - notes_before_post_set).pop()
        self.assertIsNotNone(created_note)
        note = Note.objects.get(slug=created_note.slug)
        self.assertEqual(note.title, self.form_data['title'])
        self.assertEqual(note.text, self.form_data['text'])
        self.assertEqual(note.slug, self.form_data['slug'])
        self.assertEqual(note.author, self.user)


class TestNoteEditDeleteUseNotUniqueSlug(TestCase):
    NOTE_TITLE = 'Test Title'
    NOTE_TEXT = 'Test Text'
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
            slug=NOTE_SLUG_FOR_TEST,
        )
        cls.form_data = {
            'title': cls.NEW_NOTE_TITLE,
            'text': cls.NEW_NOTE_TEXT,
            'slug': cls.NEW_NOTE_SLUG,
        }

    def test_user_cant_use_not_unique_slug(self):
        notes_before_post_set = set(Note.objects.all())
        self.assertFormError(
            self.author_client.post(
                ADD_URL,
                data={
                    'title': self.NEW_NOTE_TITLE,
                    'text': self.NEW_NOTE_TEXT,
                    'slug': NOTE_SLUG_FOR_TEST,
                }
            ),
            form='form',
            field='slug',
            errors=NOTE_SLUG_FOR_TEST + WARNING
        )
        notes_after_post_set = set(Note.objects.all())
        self.assertQuerysetEqual(notes_before_post_set, notes_after_post_set)

    def test_empty_slug(self):
        notes_before_post_set = set(Note.objects.all())
        response = self.author_client.post(
            ADD_URL,
            data={
                'title': self.NEW_NOTE_TITLE,
                'text': self.NEW_NOTE_TEXT,
            }
        )
        notes_after_post_set = set(Note.objects.all())
        self.assertRedirects(response, SUCCESS_URL)
        created_note = (notes_after_post_set - notes_before_post_set).pop()
        self.assertIsNotNone(created_note)
        note = Note.objects.get(slug=created_note.slug)
        self.assertEqual(note.slug, slugify(self.NEW_NOTE_TITLE))
        self.assertEqual(note.title, self.NEW_NOTE_TITLE)
        self.assertEqual(note.text, self.NEW_NOTE_TEXT)
        self.assertEqual(note.author, self.author)

    def test_author_can_delete_note(self):
        count_notes_before_post = Note.objects.count()
        self.assertRedirects(
            self.author_client.delete(DELETE_URL),
            SUCCESS_URL
        )
        count_notes_after_post = Note.objects.count()
        self.assertEqual(count_notes_before_post - 1, count_notes_after_post)

    def test_user_cant_delete_comment_of_another_user(self):
        notes_before_post_set = set(Note.objects.all())
        self.assertEqual(
            self.reader_client.delete(DELETE_URL).status_code,
            HTTPStatus.NOT_FOUND
        )
        notes_after_post_set = set(Note.objects.all())
        self.assertEqual(notes_after_post_set, notes_before_post_set)

    def test_author_can_edit_comment(self):
        note_before_post = Note.objects.get(slug=NOTE_SLUG_FOR_TEST)
        self.assertRedirects(
            self.author_client.post(EDIT_URL, data=self.form_data),
            SUCCESS_URL
        )
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, self.form_data['title'])
        self.assertNotEqual(self.note.title, note_before_post.title)
        self.assertEqual(self.note.text, self.form_data['text'])
        self.assertNotEqual(self.note.text, note_before_post.text)
        self.assertEqual(self.note.slug, self.form_data['slug'])
        self.assertNotEqual(self.note.slug, note_before_post.slug)
        self.assertEqual(self.note.author, self.author)

    def test_user_cant_edit_comment_of_another_user(self):
        note_before_post = Note.objects.get(slug=NOTE_SLUG_FOR_TEST)
        self.assertEqual(
            self.reader_client.post(
                EDIT_URL, data=self.form_data
            ).status_code,
            HTTPStatus.NOT_FOUND
        )
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, note_before_post.title)
        self.assertEqual(self.note.text, note_before_post.text)
        self.assertEqual(self.note.slug, note_before_post.slug)
        self.assertEqual(self.note.author, note_before_post.author)
