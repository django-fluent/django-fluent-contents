from django.db.models import Q
from parler.managers import TranslatableManager, TranslatableQuerySet
from . import appsettings


class SharedContentQuerySet(TranslatableQuerySet):
    """
    The QuerySet for SharedContent models.
    """
    
    def parent_site(self, site):
        """
        Filter to the given site, only give content relevant for that site.
        """
        if appsettings.FLUENT_SHARED_CONTENT_ENABLE_CROSS_SITE:
            # Allow content to be shared between all sites:
            return self.filter(Q(parent_site=site) | Q(is_cross_site=True))
        else:
            return self.filter(parent_site=site)


class SharedContentManager(TranslatableManager):
    """
    Extra methods attached to ``SharedContent.objects`` .
    """
    queryset_class = SharedContentQuerySet

    def parent_site(self, site):
        """
        Filter to the given site, only give content relevant for that site.
        """
        return self.get_query_set().parent_site(site)
