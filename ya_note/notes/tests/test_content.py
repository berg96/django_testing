from django.test import Client, TestCase
from django.urls import reverse

from notes.forms import NoteForm
from notes.models import Note, User


NOTE_SLUG_FOR_TEST = 'test_slug'
LIST_URL = reverse('notes:list')
ADD_URL = reverse('notes:add')
EDIT_URL = reverse('notes:edit', args=(NOTE_SLUG_FOR_TEST,))


class TestContent(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='IamGroot')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.reader = User.objects.create(username='IceFrog')
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        Note.objects.bulk_create(
            Note(
                title=f'Note{index}',
                text='Pro100 Text',
                author=cls.author,
                slug=f'note{index}'
            )
            for index in range(2)
        )
        cls.note = Note.objects.create(
            title='Test title',
            text='Test text',
            author=cls.author,
            slug=NOTE_SLUG_FOR_TEST,
        )

    def test_notes_count(self):
        self.assertEqual(
            len(self.author_client.get(LIST_URL).context['object_list']),
            Note.objects.count()
        )

    def test_notes_list_for_different_users(self):
        clients_availability = (
            (self.author_client, True),
            (self.reader_client, False)
        )
        for parametrized_client, availability in clients_availability:
            with self.subTest(client=parametrized_client):
                self.assertEqual(
                    (self.note in parametrized_client.get(
                        LIST_URL
                    ).context['object_list']),
                    availability
                )

    def test_pages_contains_form(self):
        for url in (ADD_URL, EDIT_URL):
            context = self.author_client.get(url).context
            self.assertIn('form', context)
            self.assertIsInstance(context['form'], NoteForm)
