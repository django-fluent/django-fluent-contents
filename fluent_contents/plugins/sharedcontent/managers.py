from parler.managers import TranslatableManager, TranslatableQuerySet


class SharedContentQuerySet(TranslatableQuerySet):
    """
    The QuerySet for SharedContent models.
    """

    def parent_site(self, site):
        """
        Filter to the given site.
        """
        return self.filter(parent_site=site)


class SharedContentManager(TranslatableManager):
    """
    Extra methods attached to ``SharedContent.objects`` .
    """
    queryset_class = SharedContentQuerySet

    def parent_site(self, site):
        """
        Filter to the given site.
        """
        return self.get_query_set().parent_site(site)
