from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("text", "0001_initial")]

    operations = [
        migrations.AddField(
            model_name="textitem",
            name="text_final",
            field=models.TextField(null=True, editable=False, blank=True),
            preserve_default=True,
        )
    ]
