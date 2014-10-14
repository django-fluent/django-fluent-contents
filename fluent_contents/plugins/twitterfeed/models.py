from future.utils import python_2_unicode_compatible
from django.db import models
from django.utils.translation import ugettext_lazy as _
from fluent_contents.models.db import ContentItem


@python_2_unicode_compatible
class TwitterRecentEntriesItem(ContentItem):
    """
    Content item to display recent entries of a twitter user.
    """
    title = models.CharField(_('Title'), max_length=200, blank=True, help_text=_('You may use Twitter markup here, such as a #hashtag or @username.'))

    twitter_user = models.CharField(_('Twitter user'), max_length=75)
    amount = models.PositiveSmallIntegerField(_('Number of results'), default=5)

    footer_text = models.CharField(_('Footer text'), max_length=200, blank=True, help_text=_('You may use Twitter markup here, such as a #hashtag or @username.'))
    include_retweets = models.BooleanField(_("Include retweets"), default=False)
    include_replies = models.BooleanField(_("Include replies"), default=False)

    def __str__(self):
        return self.title or self.twitter_user

    class Meta:
        verbose_name = _('Recent twitter entries')
        verbose_name_plural = _('Recent twitter entries')


@python_2_unicode_compatible
class TwitterSearchItem(ContentItem):
    """
    Content item to display recent entries of a twitter user.
    """
    title = models.CharField(_('Title'), max_length=200, blank=True, help_text=_('You may use Twitter markup here, such as a #hashtag or @username.'))

    query = models.CharField(_('Search for'), max_length=200, default='', help_text=_('<a href="https://support.twitter.com/articles/71577" target="_blank">Twitter search syntax</a> is allowed.'))
    amount = models.PositiveSmallIntegerField(_('Number of results'), default=5)

    footer_text = models.CharField(_('Footer text'), max_length=200, blank=True, help_text=_('You may use Twitter markup here, such as a #hashtag or @username.'))
    include_retweets = models.BooleanField(_("Include retweets"), default=False)
    include_replies = models.BooleanField(_("Include replies"), default=False)

    def __str__(self):
        return self.title or self.query

    class Meta:
        verbose_name = _('Twitter search feed')
        verbose_name_plural = _('Twitter search feed')
