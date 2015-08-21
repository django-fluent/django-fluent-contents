"""
Test suite for fluent-contents
"""

# All files starting with test_ are found by DiscoverRunner
# This is to make sure these are also found by Django 1.4/1.5:
from .test_admin import AdminTest
from .test_rendering import RenderingTests
from .test_templatetags import TemplateTagTests
