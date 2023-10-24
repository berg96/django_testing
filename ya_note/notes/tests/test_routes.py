from http import HTTPStatus

from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note, User


NOTE_SLUG_FOR_TEST = 'test_slug'
HOME_URL = reverse('notes:home')
LIST_URL = reverse('notes:list')
ADD_URL = reverse('notes:add')
SUCCESS_URL = reverse('notes:success')
DETAIL_URL = reverse('notes:detail', args=(NOTE_SLUG_FOR_TEST,))
EDIT_URL = reverse('notes:edit', args=(NOTE_SLUG_FOR_TEST,))
DELETE_URL = reverse('notes:delete', args=(NOTE_SLUG_FOR_TEST,))
LOGIN_URL = reverse('users:login')
LOGOUT_URL = reverse('users:logout')
SIGNUP_URL = reverse('users:signup')


class TestRoutes(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='IceFrog')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.reader = User.objects.create(username='IamGroot')
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        cls.note = Note.objects.create(
            title='Test title',
            text='Test text',
            author=cls.author,
            slug=NOTE_SLUG_FOR_TEST,
        )

    def test_pages_availability(self):
        URL_PARAM_CLIENT_EXPECTED_STATUS = [
            [HOME_URL, self.client, HTTPStatus.OK],
            [LOGIN_URL, self.client, HTTPStatus.OK],
            [LOGOUT_URL, self.client, HTTPStatus.OK],
            [SIGNUP_URL, self.client, HTTPStatus.OK],
            [LIST_URL, self.author_client, HTTPStatus.OK],
            [ADD_URL, self.author_client, HTTPStatus.OK],
            [SUCCESS_URL, self.author_client, HTTPStatus.OK],
            [DETAIL_URL, self.author_client, HTTPStatus.OK],
            [EDIT_URL, self.author_client, HTTPStatus.OK],
            [DELETE_URL, self.author_client, HTTPStatus.OK],
            [DETAIL_URL, self.reader_client, HTTPStatus.NOT_FOUND],
            [EDIT_URL, self.reader_client, HTTPStatus.NOT_FOUND],
            [DELETE_URL, self.reader_client, HTTPStatus.NOT_FOUND],
        ]
        for (
            url, parametrized_client, expected_status
        ) in URL_PARAM_CLIENT_EXPECTED_STATUS:
            with self.subTest(name=url):
                self.assertEqual(
                    parametrized_client.get(url).status_code,
                    expected_status
                )

    def test_redirect_for_anonymous_client(self):
        for url, expected_redirect in (
                (ADD_URL, f'{LOGIN_URL}?next={ADD_URL}'),
                (LIST_URL, f'{LOGIN_URL}?next={LIST_URL}'),
                (SUCCESS_URL, f'{LOGIN_URL}?next={SUCCESS_URL}'),
                (DETAIL_URL, f'{LOGIN_URL}?next={DETAIL_URL}'),
                (EDIT_URL, f'{LOGIN_URL}?next={EDIT_URL}'),
                (DELETE_URL, f'{LOGIN_URL}?next={DELETE_URL}'),
        ):
            with self.subTest(name=url):
                self.assertRedirects(self.client.get(url), expected_redirect)
