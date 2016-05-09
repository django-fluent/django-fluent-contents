from django.conf import settings
from django.db.models import Q
from parler.managers import TranslatableManager, TranslatableQuerySet
from fluent_contents import appsettings
from fluent_contents.plugins.sharedcontent import appsettings as sharedcontent_appsettings


class SharedContentQuerySet(TranslatableQuerySet):
    """
    The QuerySet for SharedContent models.
    """

    def __init__(self, *args, **kwargs):
        super(SharedContentQuerySet, self).__init__(*args, **kwargs)
        self._parent_site = None

    def _clone(self, klass=None, setup=False, **kw):
        c = super(SharedContentQuerySet, self)._clone(klass, setup, **kw)
        c._parent_site = self._parent_site
        return c

    def parent_site(self, site):
        """
        Filter to the given site, only give content relevant for that site.
        """
        # Avoid auto filter if site is already set.
        self._parent_site = site

        if sharedcontent_appsettings.FLUENT_SHARED_CONTENT_ENABLE_CROSS_SITE:
            # Allow content to be shared between all sites:
            return self.filter(Q(parent_site=site) | Q(is_cross_site=True))
        else:
            return self.filter(parent_site=site)

    def _single_site(self):
        """
        Make sure the queryset is filtered on a parent site, if that didn't happen already.
        """
        if appsettings.FLUENT_CONTENTS_FILTER_SITE_ID and self._parent_site is None:
            return self.parent_site(settings.SITE_ID)
        else:
            return self

    def get_for_slug(self, slug):
        """
        .. versionadded:: 1.0 Return the content for the given slug.
        """
        return self._single_site().get(slug=slug)


class SharedContentManager(TranslatableManager):
    """
    Extra methods attached to ``SharedContent.objects`` .
    """
    queryset_class = SharedContentQuerySet

    # This code uses calls to .all() to get the queryset
    # object in a Django 1.4-1.7 compatible way.

    def parent_site(self, site):
        """
        Filter to the given site, only give content relevant for that site.
        """
        return self.all().parent_site(site)

    def published(self):
        """
        Only show active items, meaning the current site.
        """
        # Work in the same was as all other fluent-apps do.
        return self.all()._single_site()

    def get_for_slug(self, slug):
        """
        .. versionadded:: 1.0 Return the content for the given slug.
        """
        return self.all().get_for_slug(slug=slug)
