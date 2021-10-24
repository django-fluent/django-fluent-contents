from django.db import models, transaction
from django.urls import reverse
from mptt.models import MPTTModel
from simplecms import appconfig

from fluent_contents.models import ContentItemRelation, PlaceholderRelation


class Page(MPTTModel):
    title = models.CharField("Title", max_length=200)

    # The basic fields to make the url structure work:
    slug = models.SlugField("Slug")
    parent = models.ForeignKey(
        "self", related_name="children", blank=True, null=True, on_delete=models.CASCADE
    )
    _cached_url = models.CharField(
        max_length=300, blank=True, editable=False, default="", db_index=True
    )

    # Allow different layouts
    template_name = models.CharField(
        "Layout",
        max_length=255,
        choices=appconfig.SIMPLECMS_TEMPLATE_CHOICES,
        default=appconfig.SIMPLECMS_DEFAULT_TEMPLATE,
    )

    # Accessing the data of django-fluent-contents
    placeholder_set = PlaceholderRelation()
    contentitem_set = ContentItemRelation()

    class Meta:
        verbose_name = "Page"
        verbose_name_plural = "Pages"

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        # cached_url always points to the URL within the URL config root.
        # when the application is mounted at a subfolder, or the 'cms.urls' config
        # is included at a sublevel, it needs to be prepended.
        root = reverse("simplecms-page").rstrip("/")
        return root + self._cached_url

    # ---- updating _cached_url:

    # This block of code is largely inspired and based on FeinCMS
    # (c) Matthias Kestenholz, BSD licensed

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._original_cached_url = self._cached_url

    # This code runs in a transaction since it's potentially editing a lot of records (all decendant urls).
    @transaction.atomic
    def save(self, *args, **kwargs):
        """
        Save the model, and update caches.
        """
        # Store this object
        self._make_slug_unique()
        self._update_cached_url()
        super().save(*args, **kwargs)

        # Update others
        self._update_decendant_urls()
        return super().save(*args, **kwargs)

    # Following of the principles for "clean code"
    # the save() method is split in the 3 methods below,
    # each "do one thing, and only one thing".

    def _make_slug_unique(self):
        """
        Check for duplicate slugs at the same level, and make the current object unique.
        """
        origslug = self.slug
        dupnr = 1
        while True:
            others = Page.objects.filter(parent=self.parent, slug=self.slug)
            if self.pk:
                others = others.exclude(pk=self.pk)

            if not others.count():
                break

            dupnr += 1
            self.slug = "%s-%d" % (origslug, dupnr)

    def _update_cached_url(self):
        """
        Update the URLs
        """
        # determine own URL
        if self.is_root_node():
            self._cached_url = "/%s/" % self.slug
        else:
            self._cached_url = f"{self.parent._cached_url}{self.slug}/"

    def _update_decendant_urls(self):
        """
        Update the URLs of all decendant pages.
        """
        # Performance optimisation: avoid traversing and updating many records
        # when nothing changed in the URL.
        if self._cached_url == self._original_cached_url:
            return

        # Keep cache
        cached_page_urls = {self.id: self._cached_url}

        # Update all sub objects
        subobjects = self.get_descendants().order_by("lft")
        for subobject in subobjects:
            # Set URL, using cache for parent URL.
            subobject._cached_url = "{}{}/".format(
                cached_page_urls[subobject.parent_id],
                subobject.slug,
            )
            cached_page_urls[subobject.id] = subobject._cached_url

            # call base class, do not recurse
            super(Page, subobject).save()
