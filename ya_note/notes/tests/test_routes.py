from http import HTTPStatus

from django.test import TestCase
from django.urls import reverse

from notes.models import Note, User


class TestRoutes(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='IceFrog')
        cls.reader = User.objects.create(username='IamGroot')
        cls.note = Note.objects.create(
            title='title',
            text='text',
            author=cls.author,
        )

    def test_pages_availability(self):
        for name in (
                'notes:home',
                'users:login',
                'users:logout',
                'users:signup',
        ):
            with self.subTest(name=name):
                self.assertEqual(
                    self.client.get(reverse(name)).status_code, HTTPStatus.OK
                )

    def test_pages_availability_for_auth_user(self):
        self.client.force_login(self.author)
        for name in (
            'notes:list',
            'notes:add',
            'notes:success',
        ):
            with self.subTest(name=name):
                self.assertEqual(
                    self.client.get(reverse(name)).status_code, HTTPStatus.OK
                )

    def test_availability_for_detail_edit_and_delete(self):
        users_statuses = (
            (self.author, HTTPStatus.OK),
            (self.reader, HTTPStatus.NOT_FOUND),
        )
        for user, status in users_statuses:
            self.client.force_login(user)
            for name in (
                    'notes:detail',
                    'notes:edit',
                    'notes:delete',
            ):
                with self.subTest(user=user, name=name):
                    self.assertEqual(
                        self.client.get(reverse(
                            name, args=(self.note.slug,)
                        )).status_code,
                        status
                    )

    def test_redirect_for_anonymous_client(self):
        for name, args in (
                ('notes:add', None),
                ('notes:list', None),
                ('notes:success', None),
                ('notes:detail', (self.note.slug,)),
                ('notes:edit', (self.note.slug,)),
                ('notes:delete', (self.note.slug,)),
        ):
            with self.subTest(name=name):
                self.assertRedirects(
                    self.client.get(reverse(name, args=args)),
                    f'{reverse("users:login")}?next={reverse(name, args=args)}'
                )
