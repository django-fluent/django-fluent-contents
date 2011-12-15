"""
Analyze the templates for placeholders of this module.
"""
from template_analyzer.djangoanalyzer import get_node_instances
from content_placeholders.models import PlaceholderData
from content_placeholders.templatetags.placeholder_tags import PagePlaceholderNode


def get_template_placeholder_data(template):
    """
    Return the placeholders found in a template,
    wrapped in a :class:`~content_placeholders.models.containers.PlaceholderData` object.
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
        )

        if data.slot not in names:
            result.append(data)
            names.add(data.slot)

    return result
