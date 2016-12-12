from django import template
from django.template import loader
from django.template.loader import render_to_string

register = template.Library()

@register.simple_tag(takes_context=True)
def render_comments(context, parent_item, template='comments/comments.html'):
    if not callable(getattr(template, 'render', None)):
        template_names = template if isinstance(template, (list, tuple)) else [template]
        template = loader.select_template(template_names)
    
    # Update the our new context to allow the user to override these items
    comments_context = {
        'parent_item': parent_item
    }
    comments_context.update(context)
    
    return loader.render_to_string(template, comments_context)
