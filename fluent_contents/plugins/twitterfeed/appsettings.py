"""
Settings for the twitterfeed item.
"""
from django.conf import settings

FLUENT_TWITTERFEED_AVATAR_SIZE = getattr(settings, "FLUENT_TWITTERFEED_AVATAR_SIZE", 32)
FLUENT_TWITTERFEED_REFRESH_INTERVAL = getattr(settings, "FLUENT_TWITTERFEED_REFRESH_INTERVAL", 0)
FLUENT_TWITTERFEED_TEXT_TEMPLATE = getattr(settings, "FLUENT_TWITTERFEED_TEXT_TEMPLATE", "{avatar}{text} {time}")


# The text template can hold any variable of the JavaScript extract_template_data() function,
# However, the most relevent fields are:
#
# {screen_name}
# {avatar}
# {text}
# {time}  (the relative time)
# {user_url}
# {tweet_url}
