# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.db import models, migrations
import fluent_contents.plugins.sharedcontent.utils
import fluent_contents.models.mixins


def make_site(apps, schema_editor):
    Site = apps.get_model("sites", "Site")
    Site.objects.get_or_create(
        pk=settings.SITE_ID,
        defaults=dict(
            name='example',
            domain='example.com',
        ))


def remove_site(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('sites', '0001_initial'),
        ('fluent_contents', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(make_site, reverse_code=remove_site),
        migrations.CreateModel(
            name='SharedContent',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('slug', models.SlugField(help_text='This unique name can be used refer to this content in in templates.', verbose_name='Template code')),
                ('is_cross_site', models.BooleanField(default=False, help_text='This allows contents can be shared between multiple sites in this project.<br>\nMake sure that any URLs in the content work with all sites where the content is displayed.', verbose_name='Share between all sites')),
                ('parent_site', models.ForeignKey(default=fluent_contents.plugins.sharedcontent.utils.get_current_site_id, editable=False, to='sites.Site')),
            ],
            options={
                'ordering': ('slug',),
                'verbose_name': 'Shared content',
                'verbose_name_plural': 'Shared content',
            },
            bases=(fluent_contents.models.mixins.CachedModelMixin, models.Model),
        ),
        migrations.CreateModel(
            name='SharedContentItem',
            fields=[
                ('contentitem_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='fluent_contents.ContentItem')),
                ('shared_content', models.ForeignKey(related_name='shared_content_items', verbose_name='Shared content', to='sharedcontent.SharedContent')),
            ],
            options={
                'db_table': 'contentitem_sharedcontent_sharedcontentitem',
                'verbose_name': 'Shared content',
                'verbose_name_plural': 'Shared content',
            },
            bases=('fluent_contents.contentitem',),
        ),
        migrations.CreateModel(
            name='SharedContentTranslation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('language_code', models.CharField(max_length=15, verbose_name='Language', db_index=True)),
                ('title', models.CharField(max_length=200, verbose_name='Title')),
                ('master', models.ForeignKey(related_name='translations', editable=False, to='sharedcontent.SharedContent', null=True)),
            ],
            options={
                'managed': True,
                'db_table': 'sharedcontent_sharedcontent_translation',
                'db_tablespace': '',
                'default_permissions': (),
                'verbose_name': 'Shared content Translation',
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='sharedcontenttranslation',
            unique_together=set([('language_code', 'master')]),
        ),
        migrations.AlterUniqueTogether(
            name='sharedcontent',
            unique_together=set([('parent_site', 'slug')]),
        ),
    ]
