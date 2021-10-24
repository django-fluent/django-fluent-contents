from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("form_designer", "__first__"), ("fluent_contents", "0001_initial")]

    operations = [
        migrations.CreateModel(
            name="FormDesignerLink",
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
                    "form_definition",
                    models.ForeignKey(
                        verbose_name="Form",
                        on_delete=models.PROTECT,
                        to="form_designer.FormDefinition",
                    ),
                ),
            ],
            options={
                "db_table": "contentitem_formdesignerlink_formdesignerlink",
                "verbose_name": "Form link",
                "verbose_name_plural": "Form links",
            },
            bases=("fluent_contents.contentitem",),
        )
    ]
