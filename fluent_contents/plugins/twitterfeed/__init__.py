VERSION = (0, 1, 0)

# Do some version checking
try:
    import twitter_text
except ImportError:
    raise ImportError("The 'twitter-text-py' package is required to use the 'twitterfeed' plugin.")
