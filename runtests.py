#!/usr/bin/env python
import sys
import django
from django.conf import settings, global_settings as default_settings
from django.core.management import execute_from_command_line

if not settings.configured:
    settings.configure(
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
            }
        },
        TEMPLATE_LOADERS = (
            'django.template.loaders.app_directories.Loader',
        ),
        TEMPLATE_CONTEXT_PROCESSORS = default_settings.TEMPLATE_CONTEXT_PROCESSORS + (
            'django.core.context_processors.request',
        ),
        INSTALLED_APPS = (
            'django.contrib.auth',
            'django.contrib.contenttypes',
            'django.contrib.messages',
            'django.contrib.sites',
            'django.contrib.admin',
            'fluent_contents',
            #'fluent_contents.plugins.code',
            'fluent_contents.plugins.commentsarea',
            #'fluent_contents.plugins.disquswidgets',
            #'fluent_contents.plugins.formdesignerlink',
            'fluent_contents.plugins.gist',
            'fluent_contents.plugins.googledocsviewer',
            'fluent_contents.plugins.iframe',
            #'fluent_contents.plugins.markup',
            #'fluent_contents.plugins.oembeditem',
            'fluent_contents.plugins.picture',
            'fluent_contents.plugins.rawhtml',
            'fluent_contents.plugins.sharedcontent',
            'fluent_contents.plugins.text',
            #'fluent_contents.plugins.twitterfeed',
            #'disqus',
            'django_wysiwyg',
            #'form_designer',
            'fluent_contents.tests.testapp',
        ),
        MIDDLEWARE_CLASSES = (
            'django.middleware.common.CommonMiddleware',
            'django.contrib.sessions.middleware.SessionMiddleware',
            'django.middleware.csrf.CsrfViewMiddleware',
            'django.contrib.auth.middleware.AuthenticationMiddleware',
        ),
        ROOT_URLCONF = 'fluent_contents.tests.testapp.urls',
        TEST_RUNNER = 'django.test.simple.DjangoTestSuiteRunner' if django.VERSION < (1,6) else 'django.test.runner.DiscoverRunner',
        SITE_ID = 3,
        FLUENT_CONTENTS_CACHE_OUTPUT = True,
        FLUENT_CONTENTS_CACHE_PLACEHOLDER_OUTPUT = True,
        #DISQUS_API_KEY = 'test',
        #DISQUS_WEBSITE_SHORTNAME = 'test',
        STATIC_URL = '/static/',
    )

if django.VERSION < (1,6):
    # Different test runner, needs to name all apps,
    # it doesn't locate a tests*.py in each subfolder.
    DEFAULT_TEST_APPS = [
        'fluent_contents',
        'text',
    ]
else:
    DEFAULT_TEST_APPS = [
        'fluent_contents',
    ]


def runtests():
    other_args = list(filter(lambda arg: arg.startswith('-'), sys.argv[1:]))
    test_apps = list(filter(lambda arg: not arg.startswith('-'), sys.argv[1:])) or DEFAULT_TEST_APPS
    argv = sys.argv[:1] + ['test', '--traceback'] + other_args + test_apps
    execute_from_command_line(argv)

if __name__ == '__main__':
    runtests()
