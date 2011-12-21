#!/usr/bin/env python
from setuptools import setup, find_packages
from os.path import dirname, join

setup(
    name='django-fluent-contents',
    version='0.8.0dev',
    license='Apache License, Version 2.0',

    install_requires=[
        'Django>=1.3.0',   # Using staticfiles
        'django-polymorphic>=0.2',
        'django-template-analyzer>=1.0.0',
    ],
    extras_require = {
        'code': ['Pygments'],
        'disquswidgets': ['django-disqus'],
        'formdesignerlink': ['django-form-designer'],
        'markup': ['docutils', 'textile', 'Markdown>=1.7'],
        'text': ['django-wysiwyg>=0.3.0'],
    },
    dependency_links = [
        'git+https://github.com/philomat/django-form-designer.git#egg=django-form-designer',
    ],

    description='A widget engine to display various content on Django pages',
    long_description=open(join(dirname(__file__), 'README.rst')).read(),

    author='Diederik van der Boor',
    author_email='opensource@edoburu.nl',

    url='https://github.com/edoburu/django-fluent-contents',
    download_url='https://github.com/edoburu/django-fluent-contents/zipball/master',

    packages=find_packages(exclude=('example*',)),
    include_package_data=True,

    zip_safe=False,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Framework :: Django',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
    ]
)
