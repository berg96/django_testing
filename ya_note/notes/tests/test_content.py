from django.test import TestCase
from django.urls import reverse

from notes.models import Note, User


class TestContent(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='IamGroot')
        cls.reader = User.objects.create(username='IceFrog')
        Note.objects.bulk_create(
            Note(
                title=f'Note{index}',
                text='Pro100 Text',
                author=cls.author,
                slug=f'note{index}'
            )
            for index in range(2)
        )
        cls.the_note = Note.objects.create(
            title='the_title',
            text='the_text',
            author=cls.author,
        )

    def test_notes_count(self):
        self.client.force_login(self.author)
        self.assertEqual(
            len(self.client.get(reverse('notes:list')).context['object_list']),
            Note.objects.count()
        )

    def test_notes_list_for_different_users(self):
        users_availability = (
            (self.author, True),
            (self.reader, False)
        )
        for user, availability in users_availability:
            self.client.force_login(user)
            with self.subTest(user=user):
                self.assertEqual(
                    (self.the_note in self.client.get(
                        reverse('notes:list')
                    ).context['object_list']),
                    availability
                )

    def test_pages_contains_form(self):
        for name, args in (
            ('notes:add', None),
            ('notes:edit', (self.the_note.slug,))
        ):
            self.client.force_login(self.author)
            self.assertIn(
                'form', self.client.get(reverse(name, args=args)).context
            )
