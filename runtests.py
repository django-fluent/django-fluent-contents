#!/usr/bin/env python
import sys
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
            'fluent_contents.tests.testapp',
        ),
        MIDDLEWARE_CLASSES = (
            'django.middleware.common.CommonMiddleware',
            'django.contrib.sessions.middleware.SessionMiddleware',
            'django.middleware.csrf.CsrfViewMiddleware',
            'django.contrib.auth.middleware.AuthenticationMiddleware',
        ),
        ROOT_URLCONF = 'fluent_contents.tests.testapp.urls',
        TEST_RUNNER='django.test.simple.DjangoTestSuiteRunner',   # for Django 1.6, see https://docs.djangoproject.com/en/dev/releases/1.6/#new-test-runner
        SITE_ID = 3,
        FLUENT_CONTENTS_CACHE_OUTPUT = True,
        FLUENT_CONTENTS_CACHE_PLACEHOLDER_OUTPUT = True,
    )

def runtests():
    argv = sys.argv[:1] + ['test', 'fluent_contents', '--traceback'] + sys.argv[1:]
    execute_from_command_line(argv)

if __name__ == '__main__':
    runtests()
