#!/usr/bin/env python
import sys
from django.conf import settings
from django.core.management import execute_from_command_line

if not settings.configured:
    settings.configure(
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
            }
        },
        INSTALLED_APPS = (
            'django.contrib.auth',
            'django.contrib.contenttypes',
            'django.contrib.messages',
            'django.contrib.sites',
            'django.contrib.admin',
            'fluent_contents',
            'fluent_contents.tests.testapp',
        ),
        ROOT_URLCONF = 'fluent_contents.tests.testapp.urls',
        TEST_RUNNER='django.test.simple.DjangoTestSuiteRunner',   # for Django 1.6, see https://docs.djangoproject.com/en/dev/releases/1.6/#new-test-runner
        SITE_ID = 3,
        FLUENT_CONTENTS_CACHE_OUTPUT = True,
    )

def runtests():
    argv = sys.argv[:1] + ['test', 'fluent_contents', '--traceback'] + sys.argv[1:]
    execute_from_command_line(argv)

if __name__ == '__main__':
    runtests()
