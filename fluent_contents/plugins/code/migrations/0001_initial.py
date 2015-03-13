# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fluent_contents', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CodeItem',
            fields=[
                ('contentitem_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='fluent_contents.ContentItem')),
                ('language', models.CharField(default=b'html', max_length=50, verbose_name='Language')),
                ('code', models.TextField(verbose_name='Code')),
                ('linenumbers', models.BooleanField(default=False, verbose_name='Show line numbers')),
            ],
            options={
                'db_table': 'contentitem_code_codeitem',
                'verbose_name': 'Code snippet',
                'verbose_name_plural': 'Code snippets',
            },
            bases=('fluent_contents.contentitem',),
        ),
    ]
