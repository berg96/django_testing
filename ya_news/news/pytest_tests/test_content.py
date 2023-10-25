import pytest
from django.conf import settings

from news.forms import CommentForm

HOME_URL = pytest.lazy_fixture('home_url')
DETAIL_URL = pytest.lazy_fixture('detail_url')


@pytest.mark.django_db
@pytest.mark.parametrize('url', (HOME_URL, ))
def test_news_count(client, news_list, url):
    assert len(
        client.get(url).context['object_list']
    ) == settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
@pytest.mark.parametrize('url', (HOME_URL, ))
def test_news_order(client, news_list, url):
    all_dates = [
        news.date for news in
        client.get(url).context['object_list']
    ]
    assert all_dates == sorted(all_dates, reverse=True)


@pytest.mark.django_db
@pytest.mark.parametrize('url', (DETAIL_URL, ))
def test_comments_order(comments_list, client, url):
    response = client.get(url)
    assert 'news' in response.context
    all_comments_datetime = [
        comment.created for comment in
        response.context['news'].comment_set.all()
    ]
    assert all_comments_datetime == sorted(all_comments_datetime)


@pytest.mark.django_db
@pytest.mark.parametrize(
    'url, parametrized_client, form_is_available',
    (
        (DETAIL_URL, pytest.lazy_fixture('admin_client'), True),
        (DETAIL_URL, pytest.lazy_fixture('client'), False),
    )
)
def test_availability_form_for_different_users(
    parametrized_client, form_is_available, url
):
    context = parametrized_client.get(url).context
    assert (
        'form' in context
    ) == form_is_available
    if form_is_available:
        assert isinstance(context['form'], CommentForm)
