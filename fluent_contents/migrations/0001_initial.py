# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ContentItem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('parent_id', models.IntegerField(null=True)),
                ('language_code', models.CharField(default='', max_length=15, editable=False, db_index=True)),
                ('sort_order', models.IntegerField(default=1, db_index=True)),
                ('parent_type', models.ForeignKey(to='contenttypes.ContentType', on_delete=models.CASCADE)),
            ],
            options={
                'ordering': ('placeholder', 'sort_order'),
                'verbose_name': 'Contentitem link',
                'verbose_name_plural': 'Contentitem links',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Placeholder',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('slot', models.SlugField(help_text='A short name to identify the placeholder in the template code.', verbose_name='Slot')),
                ('role', models.CharField(default='m', help_text='This defines where the object is used.', max_length=1, verbose_name='Role', choices=[('m', 'Main content'), ('s', 'Sidebar content'), ('r', 'Related content')])),
                ('parent_id', models.IntegerField(null=True)),
                ('title', models.CharField(max_length=255, verbose_name='Admin title', blank=True)),
                ('parent_type', models.ForeignKey(blank=True, to='contenttypes.ContentType', null=True, on_delete=models.CASCADE)),
            ],
            options={
                'verbose_name': 'Placeholder',
                'verbose_name_plural': 'Placeholders',
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='placeholder',
            unique_together=set([('parent_type', 'parent_id', 'slot')]),
        ),
        migrations.AddField(
            model_name='contentitem',
            name='placeholder',
            field=models.ForeignKey(related_name='contentitems', on_delete=django.db.models.deletion.SET_NULL, to='fluent_contents.Placeholder', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='contentitem',
            name='polymorphic_ctype',
            field=models.ForeignKey(related_name='polymorphic_fluent_contents.contentitem_set+', editable=False, to='contenttypes.ContentType', on_delete=models.CASCADE, null=True),
            preserve_default=True,
        ),
    ]
