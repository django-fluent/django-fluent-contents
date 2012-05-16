from django.template import Library
from django.utils.safestring import mark_safe
from twitter_text import TwitterText

register = Library()


@register.filter
def urlize_twitter(text):
    """
    Replace #hashtag and @username references in a tweet with HTML text.
    """
    tt = TwitterText(text)
    html = tt.autolink.auto_link()
    html = html.replace('twitter.com/search?q=', 'twitter.com/search/realtime/')
    return mark_safe(html)
