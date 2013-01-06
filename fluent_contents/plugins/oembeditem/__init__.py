VERSION = (0, 1, 0)

# Do some version checking
try:
    import micawber
except ImportError:
    raise ImportError("The 'micawber' package is required to use the 'oembeditem' plugin.")
