# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fluent_contents', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='RawHtmlItem',
            fields=[
                ('contentitem_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='fluent_contents.ContentItem')),
                ('html', models.TextField(help_text='Enter the HTML code to display, like the embed code of an online widget.', verbose_name='HTML code')),
            ],
            options={
                'db_table': 'contentitem_rawhtml_rawhtmlitem',
                'verbose_name': 'HTML code',
                'verbose_name_plural': 'HTML code',
            },
            bases=('fluent_contents.contentitem',),
        ),
    ]
