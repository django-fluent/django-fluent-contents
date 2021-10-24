from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("fluent_contents", "0001_initial")]

    operations = [
        migrations.CreateModel(
            name="DisqusCommentsAreaItem",
            fields=[
                (
                    "contentitem_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        on_delete=models.CASCADE,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="fluent_contents.ContentItem",
                    ),
                ),
                (
                    "allow_new",
                    models.BooleanField(default=True, verbose_name="Allow posting new comments"),
                ),
            ],
            options={
                "db_table": "contentitem_disquswidgets_disquscommentsareaitem",
                "verbose_name": "Disqus comments area",
                "verbose_name_plural": "Disqus comments areas",
            },
            bases=("fluent_contents.contentitem",),
        )
    ]
