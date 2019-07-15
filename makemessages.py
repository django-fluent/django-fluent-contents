#!/usr/bin/env python
import os
from os import path

import django
from django.conf import settings
from django.core.management import call_command


def main():
    if not settings.configured:
        module_root = path.dirname(path.realpath(__file__))

        settings.configure(DEBUG=False, INSTALLED_APPS=("fluent_contents",))

    django.setup()
    makemessages()


def makemessages():
    os.chdir("fluent_contents")
    call_command("makemessages", locale=("en", "nl"), verbosity=1)


if __name__ == "__main__":
    main()
