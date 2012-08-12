from django.conf import settings


# Define the source for the OEmbed provider list.
# By default, use a fixed set of providers, to avoid random other HTML content in the web site.
FLUENT_OEMBED_SOURCE = getattr(settings, 'FLUENT_OEMBED_SOURCE', 'list')   # basic, embedly, list


FLUENT_OEMBED_PROVIDER_LIST = getattr(settings, 'FLUENT_OEMBED_PROVIDER_LIST', (
    # A list of popular providers, based on Wordpress 3.4.1
    (r'http://(www\.)?youtube\.com/watch\S*',              'http://www.youtube.com/oembed'),
    (r'http://youtu\.be/\S*',                              'http://www.youtube.com/oembed'),
    (r'http://blip\.tv/\S*',                               'http://blip.tv/oembed/'),
    (r'http://(www\.)?vimeo\.com/\S*',                     'http://vimeo.com/api/oembed.json'),
    (r'http://(www\.)?dailymotion\.com/\S*',               'http://www.dailymotion.com/services/oembed'),
    (r'http://(www\.)?flickr\.com/\S*',                    'http://www.flickr.com/services/oembed/'),
    (r'http://(\S*?\.)?smugmug\.com/\S*',                  'http://api.smugmug.com/services/oembed/'),
    (r'http://(www\.)?hulu\.com/watch/\S*',                'http://www.hulu.com/api/oembed.json'),
    (r'http://(www\.)?viddler\.com/\S*',                   'http://lab.viddler.com/services/oembed/'),
    (r'http://qik\.com/\S*',                               'http://qik.com/api/oembed.json'),
    (r'http://revision3\.com/\S*',                         'http://revision3.com/api/oembed/'),
    (r'http://(www\.)?scribd\.com/\S*',                    'http://www.scribd.com/services/oembed'),
    (r'http://wordpress\.tv/\S*',                          'http://wordpress.tv/oembed/'),
    (r'http://(.+\.)?polldaddy\.com/\S*',                  'http://polldaddy.com/oembed/'),
    (r'http://(www\.)?funnyordie\.com/videos/\S*',         'http://www.funnyordie.com/oembed'),

    # Corrected Wordpress schemas, by looking at embed.ly:
    (r'https?://((www|mobile)\.)?twitter\.com/\S*?/status(es)?/\S*', 'http://api.twitter.com/1/statuses/oembed.json'),
    (r'http://[gi]\.\S*\.photobucket\.com/albums/\S*',               'http://photobucket.com/oembed'),
    (r'http://media\.photobucket\.com/groups/\S*',                   'http://photobucket.com/oembed'),

    # Additional ones found via embed.ly.
    # Note that embedly also implements providers which do not have an oembed implementation themselves.
    (r'http://www.slideshare.net/[^\/]+/\S*',   'http://www.slideshare.net/api/oembed/2'),
    (r'http://slidesha\.re/\S*',                'http://www.slideshare.net/api/oembed/2'),
    (r'http://flic\.kr/\S*',                    'http://www.flickr.com/services/oembed/'),
    (r'https?://gist.github.com/\S*',           'https://github.com/api/oembed'),

    # Manually discovered
    (r'http://(\S*\.)?yfrog\.com/\S*',                  'http://www.yfrog.com/api/oembed'),
    (r'http://www.mobypicture.com/user/\S*?/view/\S*',  'http://api.mobypicture.com/oEmbed'),
    (r'http://moby.to/\S*',                             'http://api.mobypicture.com/oEmbed'),
    (r'http://(\S+\.)imgur\.com/\S*',                   'http://api.imgur.com/oembed'),
    (r'http://instagr\.am/p/\S*',                       'http://api.instagram.com/oembed'),
    (r'http://instagram\.com/p/\S*',                    'http://api.instagram.com/oembed'),
))

# Allow to extend from the settings file
FLUENT_OEMBED_PROVIDER_LIST += tuple(getattr(settings, 'FLUENT_OEMBED_PROVIDER_LIST_EXTRA', ()))

# Embedly API key
MICAWBER_EMBEDLY_KEY = getattr(settings, 'MICAWBER_EMBEDLY_KEY', None)
