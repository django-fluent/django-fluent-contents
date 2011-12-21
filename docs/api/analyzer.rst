.. _fluent_contents.analyzer:

fluent_contents.analyzer
========================

.. For some reason, the automodule fails.
   Since it's just one function, document it manually.
   .. automodule:: fluent_contents.analyzer
   :members:

.. py:function:: get_template_placeholder_data(template)

    Return the placeholders found in a template,
    wrapped in a :class:`~fluent_contents.models.containers.PlaceholderData` object.

    This function looks for the :class:`~fluent_contents.templatetags.placeholder_tags.PagePlaceholderNode` nodes
    in the template, using the ``get_node_instances`` function of `django-template-analyzer`.
