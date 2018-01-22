# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fluent_contents', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='MarkupItem',
            fields=[
                ('contentitem_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='fluent_contents.ContentItem', on_delete=models.CASCADE)),
                ('text', models.TextField(verbose_name='markup')),
                ('language', models.CharField(db_index=True, verbose_name='Language', max_length=30, editable=False, choices=[('markdown', 'Markdown'), ('restructuredtext', 'reStructuredText'), ('textile', 'Textile')])),
            ],
            options={
                'db_table': 'contentitem_markup_markupitem',
                'verbose_name': 'Markup code',
                'verbose_name_plural': 'Markup code',
            },
            bases=('fluent_contents.contentitem',),
        ),
        migrations.CreateModel(
            name='MarkdownMarkupItem',
            fields=[
            ],
            options={
                'verbose_name': 'Markdown',
                'proxy': True,
                'verbose_name_plural': 'Markdown items',
            },
            bases=('markup.markupitem',),
        ),
        migrations.CreateModel(
            name='RestructuredtextMarkupItem',
            fields=[
            ],
            options={
                'verbose_name': 'reStructuredText',
                'proxy': True,
                'verbose_name_plural': 'reStructuredText items',
            },
            bases=('markup.markupitem',),
        ),
        migrations.CreateModel(
            name='TextileMarkupItem',
            fields=[
            ],
            options={
                'verbose_name': 'Textile',
                'proxy': True,
                'verbose_name_plural': 'Textile items',
            },
            bases=('markup.markupitem',),
        ),
    ]
