# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import fluent_contents.utils.validators


class Migration(migrations.Migration):

    dependencies = [
        ('fluent_contents', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='IframeItem',
            fields=[
                ('contentitem_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='fluent_contents.ContentItem', on_delete=models.CASCADE)),
                ('src', models.URLField(verbose_name='Page URL')),
                ('width', models.CharField(default='100%', help_text='Specify the size in pixels, or a percentage of the container area size.', max_length=10, verbose_name='Width', validators=[fluent_contents.utils.validators.validate_html_size])),
                ('height', models.CharField(default='600', help_text='Specify the size in pixels.', max_length=10, verbose_name='Height', validators=[fluent_contents.utils.validators.validate_html_size])),
            ],
            options={
                'db_table': 'contentitem_iframe_iframeitem',
                'verbose_name': 'Iframe',
                'verbose_name_plural': 'Iframes',
            },
            bases=('fluent_contents.contentitem',),
        ),
    ]
