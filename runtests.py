#!/usr/bin/env python -Wd
import sys
import warnings
from os import path

import django
from django.conf import global_settings as default_settings
from django.conf import settings
from django.core.management import execute_from_command_line

# python -Wd, or run via coverage:
warnings.simplefilter("always", DeprecationWarning)

# Give feedback on used versions
sys.stderr.write(f"Using Python version {sys.version[:5]} from {sys.executable}\n")
sys.stderr.write(
    "Using Django version {} from {}\n".format(
        django.get_version(), path.dirname(path.abspath(django.__file__))
    )
)

if not settings.configured:
    settings.configure(
        DATABASES={"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}},
        INSTALLED_APPS=(
            "django.contrib.auth",
            "django.contrib.contenttypes",
            "django.contrib.messages",
            "django.contrib.sessions",
            "django.contrib.sites",
            "django.contrib.admin",
            "fluent_contents",
            "fluent_contents.plugins.code",
            "fluent_contents.plugins.commentsarea",
            #'fluent_contents.plugins.disquswidgets',
            #'fluent_contents.plugins.formdesignerlink',
            "fluent_contents.plugins.gist",
            "fluent_contents.plugins.googledocsviewer",
            "fluent_contents.plugins.iframe",
            "fluent_contents.plugins.markup",
            "fluent_contents.plugins.oembeditem",
            "fluent_contents.plugins.picture",
            "fluent_contents.plugins.rawhtml",
            "fluent_contents.plugins.sharedcontent",
            "fluent_contents.plugins.text",
            #'fluent_contents.plugins.twitterfeed',
            #'disqus',
            "django_wysiwyg",
            #'form_designer',
            "fluent_contents.tests.testapp",
        ),
        MIDDLEWARE=(
            "django.middleware.common.CommonMiddleware",
            "django.contrib.sessions.middleware.SessionMiddleware",
            "django.middleware.csrf.CsrfViewMiddleware",
            "django.contrib.auth.middleware.AuthenticationMiddleware",
            "django.contrib.messages.middleware.MessageMiddleware",
            "fluent_contents.middleware.HttpRedirectRequestMiddleware",
        ),
        SECRET_KEY="testtest",
        TEMPLATES=[
            {
                "BACKEND": "django.template.backends.django.DjangoTemplates",
                "DIRS": (),
                "OPTIONS": {
                    "loaders": (
                        "django.template.loaders.filesystem.Loader",
                        "django.template.loaders.app_directories.Loader",
                    ),
                    "context_processors": (
                        "django.template.context_processors.debug",
                        "django.template.context_processors.i18n",
                        "django.template.context_processors.media",
                        "django.template.context_processors.request",
                        "django.template.context_processors.static",
                        "django.contrib.messages.context_processors.messages",
                        "django.contrib.auth.context_processors.auth",
                    ),
                },
            }
        ],
        ROOT_URLCONF="fluent_contents.tests.testapp.urls",
        TEST_RUNNER="django.test.runner.DiscoverRunner",
        DEFAULT_AUTO_FIELD="django.db.models.AutoField",
        SITE_ID=3,
        FLUENT_CONTENTS_CACHE_OUTPUT=True,
        FLUENT_CONTENTS_CACHE_PLACEHOLDER_OUTPUT=True,
        # DISQUS_API_KEY = 'test',
        # DISQUS_WEBSITE_SHORTNAME = 'test',
        STATIC_URL="/static/",
        SILENCED_SYSTEM_CHECKS=("fields.E210",),  # ImageField needs to have PIL/Pillow installed
    )

DEFAULT_TEST_APPS = ["fluent_contents"]


def runtests():
    other_args = list(filter(lambda arg: arg.startswith("-"), sys.argv[1:]))
    test_apps = (
        list(filter(lambda arg: not arg.startswith("-"), sys.argv[1:])) or DEFAULT_TEST_APPS
    )
    argv = sys.argv[:1] + ["test", "--traceback"] + other_args + test_apps
    execute_from_command_line(argv)


if __name__ == "__main__":
    runtests()
