from future.utils import python_2_unicode_compatible
from django.db import models
from django.utils.translation import ugettext_lazy as _
from fluent_contents.models.db import ContentItem


@python_2_unicode_compatible
class TwitterRecentEntriesItem(ContentItem):
    """
    Content item to display recent entries of a twitter user.
    """
    title = models.CharField(_('Title'), max_length=200, blank=True,
        help_text=_('You may use Twitter markup here, such as a #hashtag or @username.'))

    twitter_user = models.CharField(_('Twitter user'), max_length=75)
    amount = models.PositiveSmallIntegerField(_('Number of results'), default=5)

    widget_id = models.CharField(_('widget id'), max_length=75,
        help_text=_(u'See <a href="https://twitter.com/settings/widgets" target="_blank">https://twitter.com/settings/widgets</a> on how to obtain one'))

    footer_text = models.CharField(_('Footer text'), max_length=200, blank=True, editable=False,
        help_text=_('Deprecated: no longer used by Twitter widgets.'))
    include_retweets = models.BooleanField(_("Include retweets"), default=False, editable=False,
        help_text=_('Deprecated: no longer used by Twitter widgets.'))
    include_replies = models.BooleanField(_("Include replies"), default=False, editable=False,
        help_text=_('Deprecated: no longer used by Twitter widgets.'))

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
    title = models.CharField(_('Title'), max_length=200, blank=True,
        help_text=_('You may use Twitter markup here, such as a #hashtag or @username.'))

    query = models.CharField(_('Search for'), max_length=200, default='',
        help_text=_('Deprecated: no longer used by Twitter widgets. Define one when creating widgets.'))
    amount = models.PositiveSmallIntegerField(_('Number of results'), default=5)

    widget_id = models.CharField(_('widget id'), max_length=75,
        help_text=_(u'See <a href="https://twitter.com/settings/widgets" target="_blank">https://twitter.com/settings/widgets</a> on how to obtain one'))
    
    footer_text = models.CharField(_('Footer text'), max_length=200, blank=True, editable=False,
        help_text=_('Deprecated: no longer used by Twitter widgets.'))
    include_retweets = models.BooleanField(_("Include retweets"), default=False, editable=False,
        help_text=_('Deprecated: no longer used by Twitter widgets.'))
    include_replies = models.BooleanField(_("Include replies"), default=False, editable=False,
        help_text=_('Deprecated: no longer used by Twitter widgets.'))

    def __str__(self):
        return self.title or self.query

    class Meta:
        verbose_name = _('Twitter search feed')
        verbose_name_plural = _('Twitter search feed')
