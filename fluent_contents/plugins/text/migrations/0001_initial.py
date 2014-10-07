# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import fluent_contents.extensions.model_fields


class Migration(migrations.Migration):

    dependencies = [
        ('fluent_contents', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='TextItem',
            fields=[
                ('contentitem_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='fluent_contents.ContentItem')),
                ('text', fluent_contents.extensions.model_fields.PluginHtmlField(verbose_name='text', blank=True)),
            ],
            options={
                'verbose_name': 'Text',
                'verbose_name_plural': 'Text',
            },
            bases=('fluent_contents.contentitem',),
        ),
    ]
