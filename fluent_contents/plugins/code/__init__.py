VERSION = (0, 1, 0)

# Do some version checking
try:
    import pygments
except ImportError:
    raise ImportError("The 'pygments' package is required to use the 'code' plugin.")
