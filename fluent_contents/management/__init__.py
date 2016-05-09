import django
from django.db import DEFAULT_DB_ALIAS

if django.VERSION >= (1, 8):
    from django.core.management import CommandError

    # No longer possible, Django 1.8 always uses the actual model name.
    def update_model_prefix(model, db=DEFAULT_DB_ALIAS, verbosity=2):
        raise CommandError("This feature is no longer supported as of Django 1.8")
else:
    from django.contrib.contenttypes.models import ContentType
    from django.db.models import signals, get_models
    from django.dispatch import receiver
    from fluent_contents.models import ContentItem

    @receiver(signals.post_syncdb)
    def _on_post_syncdb(app, verbosity=2, db=DEFAULT_DB_ALIAS, **kwargs):
        """
        Prefix the ContentType objects of content items, to make them recognizable.
        Runs automatically at syncdb, and initial south model creation.
        """
        app_models = [m for m in get_models(app) if issubclass(m, ContentItem)]
        for model in app_models:
            update_model_prefix(model, verbosity=verbosity, db=db)

    def update_model_prefix(model, db=DEFAULT_DB_ALIAS, verbosity=2):
        """
        Internal function to update all model prefixes.
        """
        prefix = "content:"

        ct = ContentType.objects.get_for_model(model)
        new_name = u"{0} {1}".format(prefix, model._meta.verbose_name_raw).strip()

        if ct.name != new_name:
            # Django 1.4/1.5 compatible .save(update_fields=('name',)) look-a-like
            ContentType.objects.using(db).filter(pk=ct.id).update(name=new_name)

            if verbosity >= 1:
                print(" - Updated ContentType title for {0}.{1}".format(model._meta.app_label, model._meta.object_name))
            return True
        return False
