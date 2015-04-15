# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fluent_contents', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='PlaceholderFieldTestPage',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=200)),
            ],
            options={
                'verbose_name': 'Test page',
                'verbose_name_plural': 'Test pages',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='RawHtmlTestItem',
            fields=[
                ('contentitem_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='fluent_contents.ContentItem')),
                ('html', models.TextField(verbose_name=b'HTML code')),
            ],
            options={
                'db_table': 'contentitem_testapp_rawhtmltestitem',
                'verbose_name': 'Test HTML code',
                'verbose_name_plural': 'Test HTML codes',
            },
            bases=('fluent_contents.contentitem',),
        ),
        migrations.CreateModel(
            name='TimeoutTestItem',
            fields=[
                ('contentitem_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='fluent_contents.ContentItem')),
                ('html', models.TextField(verbose_name=b'HTML code')),
            ],
            options={
                'db_table': 'contentitem_testapp_timeouttestitem',
                'verbose_name': 'Timeout test',
                'verbose_name_plural': 'Timeout test',
            },
            bases=('fluent_contents.contentitem',),
        ),
        migrations.CreateModel(
            name='TestPage',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('contents', models.TextField(verbose_name=b'Contents')),
            ],
            options={
                'verbose_name': 'Test page',
                'verbose_name_plural': 'Test pages',
            },
            bases=(models.Model,),
        ),
    ]
