from django import template
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.template import loader
from django.template.loader import render_to_string

from ..utils import user_has_permission

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
    }
    return loader.render_to_string('comments/initialize.html', context)

@register.assignment_tag(takes_context=True)
def get_latest_version(context):
    # Since the versions were already ordered in the prefetch we just get the first one
    if context['node'].versions.count():
        return context['node'].versions.all()[0]
    return None

def _default_render_reply(**kwargs):
    return kwargs['comment'].level < kwargs['context']['max_depth']

@register.simple_tag(takes_context=True)
def render_reply(context):
    if user_has_permission(context['request'], context['parent_object'], 'can_reply_to_comment', default_function=_default_render_reply, comment=context['node'], context=context):
        return '<span class="action-trigger fake-link" data-action="reply">reply</span> -'
    return ''

@register.simple_tag(takes_context=True)
def render_edit(context):
    if user_has_permission(context['request'], context['parent_object'], 'can_edit_comment', comment=context['node']):
        return '<span class="action-trigger fake-link" data-action="edit">edit</span> -'
    return ''

@register.simple_tag(takes_context=True)
def render_delete(context):
    if user_has_permission(context['request'], context['parent_object'], 'can_delete_comment', comment=context['node']):
        return '<span class="action-trigger fake-link" data-action="delete">delete</span>'
    return ''
    
