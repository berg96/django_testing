import pytest

from django.conf import settings
from django.urls import reverse


@pytest.mark.django_db
def test_news_count(client, news_list):
    assert len(client.get(
        reverse('news:home')
    ).context['object_list']) == settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
def test_news_order(client, news_list):
    all_dates = [
        news.date for news in
        client.get(reverse('news:home')).context['object_list']
    ]
    assert all_dates == sorted(all_dates, reverse=True)


@pytest.mark.django_db
def test_comments_order(comments_list, detail_url, client):
    response = client.get(detail_url)
    assert 'news' in response.context
    all_comments = response.context['news'].comment_set.all()
    assert all_comments[0].created < all_comments[1].created


@pytest.mark.django_db
@pytest.mark.parametrize(
    'parametrized_client, form_is_available',
    (
        (pytest.lazy_fixture('admin_client'), True),
        (pytest.lazy_fixture('client'), False),
    )
)
def test_availability_form_for_different_users(
    parametrized_client, form_is_available, detail_url
):
    assert (
        'form' in parametrized_client.get(detail_url).context
    ) is form_is_available
