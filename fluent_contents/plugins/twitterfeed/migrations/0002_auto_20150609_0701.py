# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('twitterfeed', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='twitterrecententriesitem',
            name='widget_id',
            field=models.CharField(default=12345, help_text='See <a href="https://twitter.com/settings/widgets" target="_blank">https://twitter.com/settings/widgets</a> on how to obtain one', max_length=75, verbose_name='widget id'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='twittersearchitem',
            name='widget_id',
            field=models.CharField(default=12345, help_text='See <a href="https://twitter.com/settings/widgets" target="_blank">https://twitter.com/settings/widgets</a> on how to obtain one', max_length=75, verbose_name='widget id'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='twitterrecententriesitem',
            name='footer_text',
            field=models.CharField(help_text='Deprecated: no longer used by Twitter widgets.', verbose_name='Footer text', max_length=200, editable=False, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='twitterrecententriesitem',
            name='include_replies',
            field=models.BooleanField(default=False, help_text='Deprecated: no longer used by Twitter widgets.', verbose_name='Include replies', editable=False),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='twitterrecententriesitem',
            name='include_retweets',
            field=models.BooleanField(default=False, help_text='Deprecated: no longer used by Twitter widgets.', verbose_name='Include retweets', editable=False),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='twittersearchitem',
            name='footer_text',
            field=models.CharField(help_text='Deprecated: no longer used by Twitter widgets.', verbose_name='Footer text', max_length=200, editable=False, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='twittersearchitem',
            name='include_replies',
            field=models.BooleanField(default=False, help_text='Deprecated: no longer used by Twitter widgets.', verbose_name='Include replies', editable=False),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='twittersearchitem',
            name='include_retweets',
            field=models.BooleanField(default=False, help_text='Deprecated: no longer used by Twitter widgets.', verbose_name='Include retweets', editable=False),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='twittersearchitem',
            name='query',
            field=models.CharField(default=b'', help_text='Deprecated: no longer used by Twitter widgets. Define one when creating widgets.', max_length=200, verbose_name='Search for'),
            preserve_default=True,
        ),
    ]
