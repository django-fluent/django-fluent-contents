from django.template import Library
from django.utils.safestring import mark_safe
import ttp

register = Library()


@register.filter
def escape_tweet(text):
    """
    Replace #hashtag and @username references in a tweet with HTML text.
    """
    return mark_safe(ttp.Parser(max_url_length=60).parse(text).html.replace('search.twitter.com/search?q=', 'twitter.com/search/realtime/'))
