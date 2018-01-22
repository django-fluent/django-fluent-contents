# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fluent_contents', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CommentsAreaItem',
            fields=[
                ('contentitem_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='fluent_contents.ContentItem', on_delete=models.CASCADE)),
                ('allow_new', models.BooleanField(default=True, verbose_name='Allow posting new comments')),
            ],
            options={
                'db_table': 'contentitem_commentsarea_commentsareaitem',
                'verbose_name': 'Comments area',
                'verbose_name_plural': 'Comments areas',
            },
            bases=('fluent_contents.contentitem',),
        ),
    ]
