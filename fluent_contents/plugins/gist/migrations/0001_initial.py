# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fluent_contents', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='GistItem',
            fields=[
                ('contentitem_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='fluent_contents.ContentItem', on_delete=models.CASCADE)),
                ('gist_id', models.CharField(help_text='Go to <a href="https://gist.github.com/" target="_blank">https://gist.github.com/</a> and copy the number of the Gist snippet you want to display.', max_length=128, verbose_name='Gist number')),
                ('filename', models.CharField(help_text='Leave the filename empty to display all files in the Gist.', max_length=128, verbose_name='Gist filename', blank=True)),
            ],
            options={
                'db_table': 'contentitem_gist_gistitem',
                'verbose_name': 'GitHub Gist snippet',
                'verbose_name_plural': 'GitHub Gist snippets',
            },
            bases=('fluent_contents.contentitem',),
        ),
    ]
