VERSION = (0, 1, 0)

# Do some version checking
try:
    import ttp
except ImportError:
    raise ImportError("The 'ttp' package is required to use the 'twitterfeed' plugin.")
