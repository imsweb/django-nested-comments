from django import template
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.template import loader
from django.template.loader import render_to_string

register = template.Library()

@register.simple_tag()
def initialize_comments():
    # Have to wrap in "str()" because this dictionary is going to be directly interpreted by javascript (which doesn't accept unicode).
    return str({
        'getUrl': str(reverse('load-comments')),
        'postUrl': str(reverse('post-comment')),
        'deleteUrl': str(reverse('delete-comment')),
    })
    
@register.simple_tag()
def render_comments(parent_item, **kwargs):
    # TODO: Make defaults customizable (probably via settings)
    context = {
        'ct_id': ContentType.objects.get_for_model(parent_item).id,
        'obj_id': parent_item.id,
        'initial_load': kwargs.get('initial_load', 0),
    }
    
    return loader.render_to_string('comments/initialize.html', context)
