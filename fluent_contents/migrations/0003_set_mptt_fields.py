# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


def _tree_forward(apps, schema_editor):
    from fluent_contents.models import ContentItem
    ContentItem.objects.rebuild()


def _tree_revert(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('fluent_contents', '0002_add_mptt_fields'),
    ]

    operations = [
        migrations.RunPython(
            _tree_forward,
            _tree_revert,
        )
    ]
