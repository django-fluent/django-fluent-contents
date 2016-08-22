from django.core.cache import cache


class CachedModelMixin(object):
    """
    Mixin to add cache expiration to a model.
    """
    clear_cache_on_add = False

    def save(self, *args, **kwargs):
        is_new = not self.pk or self._state.adding
        super(CachedModelMixin, self).save(*args, **kwargs)
        if not is_new or self.clear_cache_on_add:
            self.clear_cache()

    save.alters_data = True

    def delete(self, *args, **kwargs):
        deleted_pk = self.pk
        super(CachedModelMixin, self).delete(*args, **kwargs)

        # Temporary restore to allow get_cache_keys() / plugin.get_output_cache_keys() to read the PK
        self.pk = deleted_pk
        self.clear_cache()
        self.pk = None

    # Must restore these options, or risk removing with a template print statement.
    delete.alters_data = True

    def clear_cache(self):
        """
        Delete the cache keys associated with this model.
        """
        cache.delete_many(self.get_cache_keys())

    clear_cache.alters_data = True

    def get_cache_keys(self):
        """
        Get a list of all cache keys associated with this model.
        """
        raise NotImplementedError("Implement get_cache_keys() or clear_cache()")
