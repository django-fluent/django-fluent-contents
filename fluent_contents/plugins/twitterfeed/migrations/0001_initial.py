# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fluent_contents', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='TwitterRecentEntriesItem',
            fields=[
                ('contentitem_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='fluent_contents.ContentItem')),
                ('title', models.CharField(help_text='You may use Twitter markup here, such as a #hashtag or @username.', max_length=200, verbose_name='Title', blank=True)),
                ('twitter_user', models.CharField(max_length=75, verbose_name='Twitter user')),
                ('amount', models.PositiveSmallIntegerField(default=5, verbose_name='Number of results')),
                ('footer_text', models.CharField(help_text='You may use Twitter markup here, such as a #hashtag or @username.', max_length=200, verbose_name='Footer text', blank=True)),
                ('include_retweets', models.BooleanField(default=False, verbose_name='Include retweets')),
                ('include_replies', models.BooleanField(default=False, verbose_name='Include replies')),
            ],
            options={
                'db_table': 'contentitem_twitterfeed_twitterrecententriesitem',
                'verbose_name': 'Recent twitter entries',
                'verbose_name_plural': 'Recent twitter entries',
            },
            bases=('fluent_contents.contentitem',),
        ),
        migrations.CreateModel(
            name='TwitterSearchItem',
            fields=[
                ('contentitem_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='fluent_contents.ContentItem')),
                ('title', models.CharField(help_text='You may use Twitter markup here, such as a #hashtag or @username.', max_length=200, verbose_name='Title', blank=True)),
                ('query', models.CharField(default=b'', help_text='<a href="https://support.twitter.com/articles/71577" target="_blank">Twitter search syntax</a> is allowed.', max_length=200, verbose_name='Search for')),
                ('amount', models.PositiveSmallIntegerField(default=5, verbose_name='Number of results')),
                ('footer_text', models.CharField(help_text='You may use Twitter markup here, such as a #hashtag or @username.', max_length=200, verbose_name='Footer text', blank=True)),
                ('include_retweets', models.BooleanField(default=False, verbose_name='Include retweets')),
                ('include_replies', models.BooleanField(default=False, verbose_name='Include replies')),
            ],
            options={
                'db_table': 'contentitem_twitterfeed_twittersearchitem',
                'verbose_name': 'Twitter search feed',
                'verbose_name_plural': 'Twitter search feed',
            },
            bases=('fluent_contents.contentitem',),
        ),
    ]
