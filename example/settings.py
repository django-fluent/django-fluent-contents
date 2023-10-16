# Add parent path,
# Allow starting the app without installing the module.
import sys
from os.path import dirname, join, realpath

import django

sys.path.insert(0, dirname(dirname(realpath(__file__))))

DEBUG = True

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)

MANAGERS = ADMINS

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": dirname(__file__) + "/demo.db",
    }
}

TIME_ZONE = "Europe/Amsterdam"
LANGUAGE_CODE = "en-us"
SITE_ID = 1

USE_I18N = True

MEDIA_ROOT = join(dirname(__file__), "media")
MEDIA_URL = "/media/"
STATIC_ROOT = join(dirname(__file__), "static")
STATIC_URL = "/static/"

STATICFILES_DIRS = ()
STATICFILES_FINDERS = (
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
    #    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = "-#@bi6bue%#1j)6+4b&#i0g-*xro@%f@_#zwv=2-g_@n3n_kj5"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": (join(dirname(__file__), "templates"),),
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
]

MIDDLEWARE = (
    "django.middleware.common.CommonMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
)

ROOT_URLCONF = "urls"

INSTALLED_APPS = (
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.sites",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.admin",
    "django.contrib.admindocs",
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
    "parler",
    # Example app
    "article",
    # Example CMS:
    "mptt",
    "simplecms",
    "theme1",
    # Other apps
    "django_comments",
    "django_wysiwyg",
    #'disqus',
    #'form_designer',
    "tinymce",
)

TEST_RUNNER = "django.test.runner.DiscoverRunner"

SIMPLECMS_TEMPLATE_CHOICES = (
    ("theme1/pages/standard.html", "Standard"),
    ("theme1/pages/standard-twocols.html", "Two columns"),
)
SIMPLECMS_DEFAULT_TEMPLATE = SIMPLECMS_TEMPLATE_CHOICES[0][0]

DJANGO_WYSIWYG_FLAVOR = "tinymce_advanced"

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {"require_debug_false": {"()": "django.utils.log.RequireDebugFalse"}},
    "handlers": {
        "mail_admins": {
            "level": "ERROR",
            "filters": ["require_debug_false"],
            "class": "django.utils.log.AdminEmailHandler",
        }
    },
    "loggers": {
        "django.request": {
            "handlers": ["mail_admins"],
            "level": "ERROR",
            "propagate": True,
        }
    },
}

# DISQUS_API_KEY = ''
# DISQUS_WEBSITE_SHORTNAME = ''
