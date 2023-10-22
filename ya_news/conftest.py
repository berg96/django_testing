from datetime import datetime, timedelta

import pytest
from django.conf import settings
from django.urls import reverse
from django.utils import timezone

from news.models import Comment, News


@pytest.fixture
def news():
    news = News.objects.create(
        title='Title',
        text='Text',
    )
    return news


@pytest.fixture
def id_for_news(news):
    return news.pk,


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='IamGroot')


@pytest.fixture
def author_client(author, client):
    client.force_login(author)
    return client


@pytest.fixture
def comment(author, news):
    comment = Comment.objects.create(
        news=news,
        author=author,
        text='Text',
    )
    return comment


@pytest.fixture
def id_for_comment(comment):
    return comment.pk,


@pytest.fixture
def news_list():
    today = datetime.today()
    return News.objects.bulk_create(
        News(
            title=f'Новость {index}',
            text='Просто текст.',
            date=today - timedelta(days=index)
        )
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    )


@pytest.fixture
def comments_list(news, author):
    now = timezone.now()
    for index in range(2):
        comment = Comment.objects.create(
            news=news, author=author, text=f'Tекст {index}',
        )
        comment.created = now + timedelta(days=index)
        comment.save()


@pytest.fixture
def form_data():
    return {'text': 'Pro100Text'}


@pytest.fixture
def detail_url(id_for_news):
    return reverse('news:detail', args=id_for_news)


@pytest.fixture
def delete_url(id_for_comment):
    return reverse('news:delete', args=id_for_comment)


@pytest.fixture
def edit_url(id_for_comment):
    return reverse('news:edit', args=id_for_comment)
