from django import template
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.template import loader
from django.template.loader import render_to_string

from ..utils import user_has_permission

import json

register = template.Library()

@register.simple_tag()
def initialize_comments(**kwargs):
    default_kwargs = {
        'getUrl': reverse('load-comments'),
        'postUrl': reverse('post-comment'),
        'deleteUrl': reverse('delete-comment'),
    }
    # This mirrors the values in 'comments.js' to allow them to be overridden. All other kwargs are passed through the key 'kwargs'.
    js_keys_overridden = set(kwargs.keys()).intersection(['actionTriggerSelector',
                                                          'childCommentsSelector',
                                                          'commentContainerSelector',
                                                          'commentFormSelector',
                                                          'hiddenFieldsSelector',
                                                          'messageEditContainerSelector',
                                                          'nodeContainerSelector',
                                                          'originalMessageSelector',
                                                          'postCommentLoadFunction',
                                                          'rootContainerSelector',
                                                          'getUrl',
                                                          'postUrl',
                                                          'deleteUrl'])
    for item in js_keys_overridden:
        default_kwargs[item] = kwargs.pop(item)
    # Everything left in kwargs is passed through the generic 'kwargs' key. These values will ultimately be sent back via a signal in a header.
    default_kwargs['kwargs'] = kwargs
    # This will be fed directly into javascript, so we use json.dumps to ensure it can be interpreted.
    return json.dumps(default_kwargs)
    
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

@register.simple_tag(takes_context=True)
def render_reply(context):
    comment = context['node']
    if user_has_permission(context['request'], context['parent_object'], 'can_reply_to_comment', comment=comment) and comment.level < context['max_depth']:
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
    
