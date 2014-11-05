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
            name='GoogleDocsViewerItem',
            fields=[
                ('contentitem_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='fluent_contents.ContentItem')),
                ('url', models.URLField(help_text='Specify the URL of an online document, for example a PDF or DOCX file.', verbose_name='File URL')),
                ('width', models.CharField(default=b'100%', help_text='Specify the size in pixels, or a percentage of the container area size.', max_length=10, verbose_name='Width', validators=[fluent_contents.utils.validators.validate_html_size])),
                ('height', models.CharField(default=b'600', help_text='Specify the size in pixels.', max_length=10, verbose_name='Height', validators=[fluent_contents.utils.validators.validate_html_size])),
            ],
            options={
                'db_table': 'contentitem_googledocsviewer_googledocsvieweritem',
                'verbose_name': 'Embedded document',
                'verbose_name_plural': 'Embedded document',
            },
            bases=('fluent_contents.contentitem',),
        ),
    ]
