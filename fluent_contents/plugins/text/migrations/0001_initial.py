from django.db import migrations, models

import fluent_contents.extensions.model_fields


class Migration(migrations.Migration):

    dependencies = [("fluent_contents", "0001_initial")]

    operations = [
        migrations.CreateModel(
            name="TextItem",
            fields=[
                (
                    "contentitem_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="fluent_contents.ContentItem",
                        on_delete=models.CASCADE,
                    ),
                ),
                (
                    "text",
                    fluent_contents.extensions.model_fields.PluginHtmlField(
                        verbose_name="text", blank=True
                    ),
                ),
            ],
            options={
                "db_table": "contentitem_text_textitem",
                "verbose_name": "Text",
                "verbose_name_plural": "Text",
            },
            bases=("fluent_contents.contentitem",),
        )
    ]
