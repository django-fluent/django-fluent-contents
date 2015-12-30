"""
Test suite for fluent-contents
"""
import django
if django.VERSION < (1,6):
    # Expose for Django 1.5 and below (before DiscoverRunner)
    from .test_admin import AdminTest
    from .test_rendering import RenderingTests
    from .test_search import SearchTest
    from .test_templatetags import TemplateTagTests
