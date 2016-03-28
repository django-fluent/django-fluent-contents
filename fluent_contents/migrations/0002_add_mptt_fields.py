# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fluent_contents', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='contentitem',
            options={'ordering': ('placeholder', 'tree_id', 'lft', 'sort_order'), 'verbose_name': 'Contentitem link', 'verbose_name_plural': 'Contentitem links'},
        ),
        migrations.AddField(
            model_name='contentitem',
            name='parent_item',
            field=models.ForeignKey(related_name='child_items', blank=True, to='fluent_contents.ContentItem', null=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='contentitem',
            name='level',
            field=models.PositiveIntegerField(default=0, editable=False, db_index=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='contentitem',
            name='lft',
            field=models.PositiveIntegerField(default=1, editable=False, db_index=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='contentitem',
            name='rght',
            field=models.PositiveIntegerField(default=2, editable=False, db_index=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='contentitem',
            name='tree_id',
            field=models.PositiveIntegerField(default=0, editable=False, db_index=True),
            preserve_default=False,
        ),
        migrations.CreateModel(
            name='ContainerItem',
            fields=[
            ],
            options={
                'verbose_name': 'Content Container',
                'proxy': True,
                'verbose_name_plural': 'Content Containers',
            },
            bases=('fluent_contents.contentitem',),
        ),
    ]
