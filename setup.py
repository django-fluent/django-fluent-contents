#!/usr/bin/env python
from setuptools import setup, find_packages
from os import path
import codecs
import os
import re
import sys


# When creating the sdist, make sure the django.mo file also exists:
if 'sdist' in sys.argv or 'develop' in sys.argv:
    try:
        os.chdir('fluent_contents')

        from django.core.management.commands.compilemessages import Command
        command = Command()
        command.execute(stdout=sys.stderr, verbosity=1)
    except:
        # < Django 1.7
        from django.core.management.commands.compilemessages import compile_messages
        compile_messages(sys.stderr)
    finally:
        os.chdir('..')


def read(*parts):
    file_path = path.join(path.dirname(__file__), *parts)
    return codecs.open(file_path, encoding='utf-8').read()


def find_version(*parts):
    version_file = read(*parts)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", version_file, re.M)
    if version_match:
        return str(version_match.group(1))
    raise RuntimeError("Unable to find version string.")


setup(
    name='django-fluent-contents',
    version=find_version('fluent_contents', '__init__.py'),
    license='Apache License, Version 2.0',

    install_requires=[
        'django-fluent-utils>=1.0',        # DRY utility code
        'django-parler>=1.1.1',            # Needed for Django 1.7 compatibility
        'django-polymorphic>=0.6',         # Needed for Django 1.7 compatibility
        'django-tag-parser>=2.0',
        'django-template-analyzer>=1.4',   # Needed for Django 1.7 compatibility
        'future>=0.12.2',
        'six>=1.5.2',
    ],
    requires=[
        'Django (>=1.4)',
    ],
    extras_require = {
        'code': ['Pygments'],
        'disquscommentsarea': ['django-disqus'],
        'formdesignerlink': ['django-form-designer'],
        'markup': ['docutils', 'textile', 'Markdown>=1.7'],
        'oembeditem': ['micawber>=0.2.6'],
        'text': ['django-wysiwyg>=0.5.1'],
        'twitterfeed': ['twitter-text-py>=1.0.3'],
        'picture': ['django-any-urlfield>=2.1.0', 'django-any-imagefield']
    },
    dependency_links = [
        'git+https://github.com/philomat/django-form-designer.git#egg=django-form-designer-dev',
    ],

    description='A widget engine to display various content on Django pages',
    long_description=read('README.rst'),

    author='Diederik van der Boor',
    author_email='opensource@edoburu.nl',

    url='https://github.com/edoburu/django-fluent-contents',
    download_url='https://github.com/edoburu/django-fluent-contents/zipball/master',

    packages=find_packages(exclude=('example*',)),
    include_package_data=True,

    test_suite = 'runtests',

    zip_safe=False,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)
