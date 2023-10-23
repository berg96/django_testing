from datetime import datetime, timedelta

import pytest
from django.conf import settings
from django.test import Client
from django.urls import reverse
from django.utils import timezone

from news.forms import BAD_WORDS
from news.models import Comment, News


@pytest.fixture
def news():
    return News.objects.create(
        title='Title',
        text='Text',
    )


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='IamGroot')


@pytest.fixture
def author_client(author):
    author_client = Client()
    author_client.force_login(author)
    return author_client


@pytest.fixture
def comment(author, news):
    return Comment.objects.create(
        news=news,
        author=author,
        text='Text',
    )


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
    for index in range(10):
        comment = Comment.objects.create(
            news=news, author=author, text=f'Tекст {index}',
        )
        comment.created = now + timedelta(days=index)
        comment.save()


@pytest.fixture
def form_data_for_comment():
    return {'text': 'Pro100Text'}


@pytest.fixture
def detail_url(news):
    return reverse('news:detail', args=(news.pk,))


@pytest.fixture
def delete_url(comment):
    return reverse('news:delete', args=(comment.pk,))


@pytest.fixture
def edit_url(comment):
    return reverse('news:edit', args=(comment.pk,))


@pytest.fixture
def home_url():
    return reverse('news:home')


@pytest.fixture
def login_url():
    return reverse('users:login')


@pytest.fixture
def logout_url():
    return reverse('users:logout')


@pytest.fixture
def signup_url():
    return reverse('users:signup')


@pytest.fixture
def form_data_for_comment_with_bad_word():
    return {'text': f'Text, {BAD_WORDS[0]}, etc'}
