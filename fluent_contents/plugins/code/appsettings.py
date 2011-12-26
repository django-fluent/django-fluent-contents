"""
Settings for the code plugin.
"""
from django.conf import settings

_defaultShortlist = (
    #'as',
    'as3',
    #'aspx-cs',
    #'aspx-vb',
    'bash',
    'c',
    'cpp',
    'csharp',
    'css',
    'html',
    #'html+php',
    'java',
    'js',
    #'jsp',
    'make',
    'objective-c',
    'perl',
    'php',
    'python',
    'sql',
    'ruby',
    'vb.net',
    'xml',
    'xslt',
)

FLUENT_CODE_DEFAULT_LANGUAGE = getattr(settings, "FLUENT_CODE_DEFAULT_LANGUAGE", 'html')
FLUENT_CODE_STYLE = getattr(settings, 'FLUENT_CODE_STYLE', 'default')
FLUENT_CODE_DEFAULT_LINE_NUMBERS = getattr(settings, 'FLUENT_CODE_DEFAULT_LINE_NUMBERS', False)
FLUENT_CODE_SHORTLIST = getattr(settings, 'FLUENT_CODE_SHORTLIST', _defaultShortlist)
FLUENT_CODE_SHORTLIST_ONLY = getattr(settings, 'FLUENT_CODE_SHORTLIST_ONLY', False)
