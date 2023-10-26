from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects

HOME_URL = pytest.lazy_fixture('home_url')
DETAIL_URL = pytest.lazy_fixture('detail_url')
EDIT_URL = pytest.lazy_fixture('edit_url')
DELETE_URL = pytest.lazy_fixture('delete_url')
LOGIN_URL = pytest.lazy_fixture('login_url')
LOGOUT_URL = pytest.lazy_fixture('logout_url')
SIGNUP_URL = pytest.lazy_fixture('signup_url')
ANONYMOUS = pytest.lazy_fixture('client')
AUTHOR_CLIENT = pytest.lazy_fixture('author_client')
READER_CLIENT = pytest.lazy_fixture('admin_client')
OK = HTTPStatus.OK
NOT_FOUND = HTTPStatus.NOT_FOUND


@pytest.mark.django_db
@pytest.mark.parametrize(
    'url, custom_client, expected_status',
    (
        (HOME_URL, ANONYMOUS, OK),
        (DETAIL_URL, ANONYMOUS, OK),
        (LOGIN_URL, ANONYMOUS, OK),
        (LOGOUT_URL, ANONYMOUS, OK),
        (SIGNUP_URL, ANONYMOUS, OK),
        (EDIT_URL, AUTHOR_CLIENT, OK),
        (DELETE_URL, AUTHOR_CLIENT, OK),
        (EDIT_URL, READER_CLIENT, NOT_FOUND),
        (DELETE_URL, READER_CLIENT, NOT_FOUND)
    )
)
def test_pages_availability(url, custom_client, expected_status):
    assert custom_client.get(url).status_code == expected_status


# @pytest.mark.parametrize(
#     'url, redirect_url',
#     (
#         (EDIT_URL, f'{LOGIN_URL}?next={EDIT_URL}'),
#         (DELETE_URL, f'{LOGIN_URL}?next={DELETE_URL}'),
#     )
# ) Пока не нашёл решение этой задачи
@pytest.mark.parametrize('url', (EDIT_URL, DELETE_URL,))
def test_redirect_for_anonymous_client(client, url, login_url):
    assertRedirects(client.get(url), f'{login_url}?next={url}')
