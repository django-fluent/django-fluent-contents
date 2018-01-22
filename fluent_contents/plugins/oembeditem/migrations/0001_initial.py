# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import fluent_contents.plugins.oembeditem.fields


class Migration(migrations.Migration):

    dependencies = [
        ('fluent_contents', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='OEmbedItem',
            fields=[
                ('contentitem_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='fluent_contents.ContentItem', on_delete=models.CASCADE)),
                ('embed_url', fluent_contents.plugins.oembeditem.fields.OEmbedUrlField(help_text='Enter the URL of the online content to embed (e.g. a YouTube or Vimeo video, SlideShare presentation, etc..)', verbose_name='URL to embed')),
                ('embed_max_width', models.PositiveIntegerField(null=True, verbose_name='Max width', blank=True)),
                ('embed_max_height', models.PositiveIntegerField(null=True, verbose_name='Max height', blank=True)),
                ('type', models.CharField(max_length=20, null=True, editable=False, blank=True)),
                ('url', models.URLField(null=True, editable=False, blank=True)),
                ('title', models.CharField(max_length=512, null=True, editable=False, blank=True)),
                ('description', models.TextField(null=True, editable=False, blank=True)),
                ('author_name', models.CharField(max_length=255, null=True, editable=False, blank=True)),
                ('author_url', models.URLField(null=True, editable=False, blank=True)),
                ('provider_name', models.CharField(max_length=255, null=True, editable=False, blank=True)),
                ('provider_url', models.URLField(null=True, editable=False, blank=True)),
                ('thumbnail_url', models.URLField(null=True, editable=False, blank=True)),
                ('thumbnail_height', models.IntegerField(null=True, editable=False, blank=True)),
                ('thumbnail_width', models.IntegerField(null=True, editable=False, blank=True)),
                ('height', models.IntegerField(null=True, editable=False, blank=True)),
                ('width', models.IntegerField(null=True, editable=False, blank=True)),
                ('html', models.TextField(null=True, editable=False, blank=True)),
            ],
            options={
                'db_table': 'contentitem_oembeditem_oembeditem',
                'verbose_name': 'Online media',
                'verbose_name_plural': 'Online media',
            },
            bases=('fluent_contents.contentitem',),
        ),
    ]
