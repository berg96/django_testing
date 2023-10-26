import pytest
from django.conf import settings

from news.forms import CommentForm


@pytest.mark.django_db
def test_news_count(client, news_list, home_url):
    assert len(
        client.get(home_url).context['object_list']
    ) == settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
def test_news_order(client, news_list, home_url):
    all_dates = [
        news.date for news in
        client.get(home_url).context['object_list']
    ]
    assert all_dates == sorted(all_dates, reverse=True)


@pytest.mark.django_db
def test_comments_order(comments_list, client, detail_url):
    response = client.get(detail_url)
    assert 'news' in response.context
    all_comments_datetime = [
        comment.created for comment in
        response.context['news'].comment_set.all()
    ]
    assert all_comments_datetime == sorted(all_comments_datetime)


@pytest.mark.django_db
@pytest.mark.parametrize(
    'custom_client, form_is_available',
    (
        (pytest.lazy_fixture('admin_client'), True),
        (pytest.lazy_fixture('client'), False),
    )
)
def test_availability_form_for_different_users(
    custom_client, form_is_available, detail_url
):
    context = custom_client.get(detail_url).context
    assert (
        'form' in context
    ) == form_is_available
    if form_is_available:
        assert isinstance(context['form'], CommentForm)
