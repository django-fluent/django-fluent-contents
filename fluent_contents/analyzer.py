"""
Analyze the templates for placeholders of this module.
"""
from template_analyzer.djangoanalyzer import get_node_instances
from fluent_contents.models import PlaceholderData
from fluent_contents.templatetags.fluent_contents_tags import PagePlaceholderNode

__all__ = ('get_template_placeholder_data',)


def get_template_placeholder_data(template):
    """
    Return the placeholders found in a template,
    wrapped in a :class:`~fluent_contents.models.containers.PlaceholderData` object.

    This function looks for the :class:`~fluent_contents.templatetags.fluent_contents_tags.PagePlaceholderNode` nodes
    in the template, using the :func:`~template_analyzer.djangoanalyzer.get_node_instances` function
    of `django-template-analyzer <https://github.com/edoburu/django-template-analyzer>`_.

    :param template:  The Template object, or nodelist to scan.
    :rtype: list of :class:`~fluent_contents.models.PlaceholderData`
    """
    # Find the instances.
    nodes = get_node_instances(template, PagePlaceholderNode)

    # Avoid duplicates, wrap in a class.
    names = set()
    result = []
    for pageplaceholdernode in nodes:
        data = PlaceholderData(
            slot=pageplaceholdernode.get_slot(),
            title=pageplaceholdernode.get_title(),
            role=pageplaceholdernode.get_role(),
            fallback_language=pageplaceholdernode.get_fallback_language(),
        )

        if data.slot not in names:
            result.append(data)
            names.add(data.slot)

    return result
