#!/usr/bin/env python
import codecs
import os
import re
import sys
from os import path

from setuptools import find_packages, setup

# When creating the sdist, make sure the django.mo file also exists:
if "sdist" in sys.argv or "develop" in sys.argv:
    os.chdir("fluent_contents")
    try:
        from django.core import management

        management.call_command("compilemessages", stdout=sys.stderr, verbosity=1)
    except ImportError:
        if "sdist" in sys.argv:
            raise
    finally:
        os.chdir("..")


def read(*parts):
    file_path = path.join(path.dirname(__file__), *parts)
    return codecs.open(file_path, encoding="utf-8").read()


def find_version(*parts):
    version_file = read(*parts)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", version_file, re.M)
    if version_match:
        return str(version_match.group(1))
    raise RuntimeError("Unable to find version string.")


setup(
    name="django-fluent-contents",
    version=find_version("fluent_contents", "__init__.py"),
    license="Apache 2.0",
    install_requires=[
        "django-fluent-utils>=2.0.0",  # DRY utility code
        "django-parler>=2.0.1",
        "django-polymorphic>=2.1.2",
        "django-tag-parser>=3.2",
        "django-template-analyzer>=1.6.2",
        "html5lib >= 1.1",
    ],
    requires=["Django (>=2.2)"],
    extras_require={
        "code": ["Pygments"],
        "disquscommentsarea": ["django-disqus"],
        "formdesignerlink": ["django-form-designer-ai>=1.0.1"],
        "markup": ["docutils", "textile", "Markdown>=1.7"],
        "oembeditem": ["micawber>=0.3.3", "beautifulsoup4>=4.3.2"],
        "text": ["django-wysiwyg>=0.7.1"],
        "twitterfeed": ["twitter-text>=3.0"],
        "tests": [
            "django-wysiwyg",
            "html5lib",
            "Pillow",
            "micawber",
            "docutils",
            "textile",
            "MarkDown",
            "pygments",
            "disqus",
        ],
    },
    tests_require=["docutils", "textile", "Markdown>=1.7"],
    description="A widget engine to display various content on Django pages",
    long_description=read("README.rst"),
    author="Diederik van der Boor",
    author_email="opensource@edoburu.nl",
    url="https://github.com/edoburu/django-fluent-contents",
    download_url="https://github.com/edoburu/django-fluent-contents/zipball/master",
    packages=find_packages(exclude=("example*",)),
    include_package_data=True,
    test_suite="runtests",
    zip_safe=False,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Framework :: Django",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Framework :: Django",
        "Framework :: Django :: 2.2",
        "Framework :: Django :: 3.1",
        "Framework :: Django :: 3.2",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
