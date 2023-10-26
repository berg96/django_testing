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
OK = HTTPStatus.OK
NOT_FOUND = HTTPStatus.NOT_FOUND


class TestRoutes(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.guest = Client()
        cls.author_user = User.objects.create(username='IceFrog')
        cls.author = Client()
        cls.author.force_login(cls.author_user)
        cls.reader = User.objects.create(username='IamGroot')
        cls.another = Client()
        cls.another.force_login(cls.reader)
        cls.note = Note.objects.create(
            title='Test title',
            text='Test text',
            author=cls.author_user,
            slug=NOTE_SLUG_FOR_TEST,
        )

    def test_pages_availability(self):
        URL_CLIENT_EXPECTED_STATUS = [
            [HOME_URL, self.guest, OK],
            [LOGIN_URL, self.guest, OK],
            [LOGOUT_URL, self.guest, OK],
            [SIGNUP_URL, self.guest, OK],
            [LIST_URL, self.author, OK],
            [ADD_URL, self.author, OK],
            [SUCCESS_URL, self.author, OK],
            [DETAIL_URL, self.author, OK],
            [EDIT_URL, self.author, OK],
            [DELETE_URL, self.author, OK],
            [DETAIL_URL, self.another, NOT_FOUND],
            [EDIT_URL, self.another, NOT_FOUND],
            [DELETE_URL, self.another, NOT_FOUND],
        ]
        for url, client, expected_status in URL_CLIENT_EXPECTED_STATUS:
            with self.subTest(url=url, client=client, status=expected_status):
                self.assertEqual(
                    client.get(url).status_code,
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
                self.assertRedirects(self.guest.get(url), expected_redirect)
