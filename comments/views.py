from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from django.db.models.query import Prefetch
from django.http import JsonResponse
from django.http.response import Http404
from django.shortcuts import render
from django.template import loader
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_GET
from django.db import DatabaseError

from .forms import CommentVersionForm
from .models import Comment, CommentVersion
from .signals import comment_changed
from .utils import InvalidCommentException, FailSafelyException, ajax_only, _get_target_comment, _get_or_create_tree_root, _process_node_permissions, user_has_permission, get_attr_val

import json

def create_comment_without_request(obj, user, message):
    """
    This is intended for use with cron jobs. This creates a comment without using a request.
    This is only for creating a comment, not for replying or editing a comment.
    """

    comment = Comment(parent=Comment.objects.get(object_id=obj.pk), created_by=user)

    if not obj.can_post_comment(comment=comment, user=user):
        raise Exception("User can't create comments")

    # select_for_update in add_comment must be wrapped in an atomic transaction.
    with transaction.atomic():
        comment = add_comment(comment)

    # Create a new/original version of the comment.
    create_new_version_without_request(comment, message, user)

    return comment

def create_new_version_without_request(comment, message, user):
    """
    Calls new_version with the parameters to create a version without a request object. 
    """
    return new_version(comment, user, {'message':message, 'comment':comment, 'posting_user':user})

def new_version(comment, user, form_data_to_bind):
    version_form = CommentVersionForm(form_data_to_bind)
    new_version = None
    if version_form.is_valid():
        new_version = version_form.save(commit=False)
        new_version.comment = comment
        new_version.posting_user = user
        new_version.save()

    return version_form, new_version
    

def get_comment(request):
    comment, previous_version = _get_target_comment(request)
    return comment, previous_version

def user_can_post_comment(request, comment):
    parent_comment = comment.parent
    tree_root = parent_comment.get_root()
    parent_object = tree_root.content_object
    return user_has_permission(request, parent_object, 'can_post_comment', comment=comment)

def is_past_max_depth(comment):
    parent_comment = comment.parent
    tree_root = parent_comment.get_root()

    return parent_comment.level >= tree_root.max_depth

def add_comment(comment):
    # TODO: Add the ability to override "position" (default is 'last-child')
    parent_comment = comment.parent

    # We lock the parent comment to prevent a race condition when adding new comments
    lock_comment(parent_comment, False)

    return Comment.objects.insert_node(comment, parent_comment, save=True)

def lock_comment(comment, nowait=True):
    Comment.objects.select_for_update(nowait=nowait).get(pk=comment.pk)

def not_most_recent_version(comment, previous_version):
    return previous_version and previous_version != comment.versions.latest()

def create_new_version(request, comment):
    return new_version(comment, request.user, request.POST)

def get_template(request, comment, parent_object, tree_root, new_version, previous_version, send_signal=True):
    # The 'X_KWARGS' header is populated by settings.kwarg in comments.js
    kwargs = json.loads(request.headers.get('x-kwargs', {}))

    kwargs.update({
                   'node': comment,
                   'nodes': [comment], # We need both because of _process_node_permissions and the fact that 'post' requires the full comments template
                   'latest_version': comment.versions.latest(), # We need this here because the latest version is not available inside the single comment template (used for edit)
                   'parent_object': parent_object,
                   'max_depth': tree_root.max_depth
                   })

    # Now that the version has been saved, we fire off the appropriate signal before returning the rendered template
    if previous_version:
        if send_signal: comment_changed.send(sender=comment.__class__, comment=comment, request=request, version_saved=new_version, comment_action='edit', kwargs=kwargs)
        comment_template = get_attr_val(request, parent_object, 'single_comment_template', 'comments/comments.html', **kwargs)
    else:
        if send_signal: comment_changed.send(sender=comment.__class__, comment=comment, request=request, version_saved=new_version, comment_action='post', kwargs=kwargs)
        comment_template = get_attr_val(request, parent_object, 'comments_template', 'comments/comments.html', **kwargs)

    kwargs['request'] = request
    # Checks/assigns permissions to each node (so the template doesn't have to)
    _process_node_permissions(**kwargs)

    return comment_template, kwargs

def post_comment_form(request):
    """
    View function that handles inserting new comments via POST data (form submission)
    """
    try:
        comment, previous_version = get_comment(request)
    except InvalidCommentException as e:
        raise

    parent_comment = comment.parent
    tree_root = parent_comment.get_root()
    parent_object = tree_root.content_object
    if not user_can_post_comment(request, comment):
        raise Exception("User can't create comments")

    if is_past_max_depth(comment):
        raise Exception("Max depth reached")

    # If the comment object (NOT the message) hasn't been saved yet...
    if comment._state.adding == True:
       comment = add_comment(comment)

    # Everything has checked out, so we save the new version and return the appropriate response
    version_form, new_version = create_new_version(request, comment)

    return comment

@transaction.atomic
@require_POST
@ajax_only
def post_comment(request, send_signal=True):
    """
    View function that handles inserting new/editing previously existing comments via Ajax
    """
    # Based on variables passed in we get the comment the user is attempting to create/edit
    comment, previous_version = get_comment(request)

    # Check if the user doesn't pass the appropriate permission check (on the parent_object)...
    # We call this on the parent comment because the comment itself may not have been saved yet (can't call .get_root on it)
    # TODO: Fix this for root comment? (no parent)
    parent_comment = comment.parent
    tree_root = parent_comment.get_root()
    parent_object = tree_root.content_object
    if not user_can_post_comment(request, comment):
        raise FailSafelyException("You do not have permission to post this comment.")

    # Check to make sure we are not trying to save a comment "deeper" than we are allowed...
    if is_past_max_depth(comment):
        raise FailSafelyException("You cannot respond to this comment.")

    # If the comment object (NOT the message) hasn't been saved yet...
    if comment._state.adding == True:
       comment = add_comment(comment)

    # Now that we have a comment object, we get a 'lock' on it to prevent a race condition
    try:
        lock_comment(comment)
    except DatabaseError as e:
        raise FailSafelyException("Someone else is currently editing this comment. Please refresh your page and try again.") from e

    # Now we know we have sole access to the comment object at the moment so we need to check if we are editing the most recent version
    if not_most_recent_version(comment, previous_version):        
        raise FailSafelyException("You are not editing the most recent version of this comment. Please refresh your page and try again.")

    # Everything has checked out, so we save the new version and return the appropriate response
    version_form, new_version = create_new_version(request, comment)
    if not version_form.is_valid():
        raise FailSafelyException("There were errors in your submission. Please correct them and resubmit.")
    
    comment_template, kwargs = get_template(request, comment, parent_object, tree_root, new_version, previous_version, send_signal=send_signal)

    return JsonResponse({
        'ok': True,
        'html_content': loader.render_to_string(comment_template, context=kwargs, request=request)
    })    


@transaction.atomic
@require_POST
@ajax_only
def delete_comment(request):
    # Based on variables passed in we get the comment the user is attempting to create/edit
    comment, previous_version = _get_target_comment(request)

    # Check if the user doesn't pass the appropriate permission check (on the parent_object)...
    # We call this on the parent comment because the comment itself may not have been saved yet (can't call .get_root on it)
    # TODO: Fix this for root comment? (no parent)
    parent_comment = comment.parent
    tree_root = parent_comment.get_root()
    parent_object = tree_root.content_object
    if not user_has_permission(request, parent_object, 'can_delete_comment', comment=comment):
        raise FailSafelyException("You do not have permission to post this comment.")

    try:
        # The 'X_KWARGS' header is populated by settings.kwarg in comments.js
        kwargs = json.loads(request.headers.get('x-kwargs', {}))
        comment_changed.send(sender=comment.__class__, comment=comment, request=request, version_saved=None, comment_action='pre_delete', kwargs=kwargs)

        comment.deleted = True
        comment.save()
        for child in comment.get_children():
            child.deleted = True
            child.save()

        return JsonResponse({
            'ok': True,
        })
    except Exception as e:
        raise FailSafelyException('There was an error deleting the selected comment(s).') from e


@ajax_only
@require_GET
def load_comments(request):
    """
    View function that returns the comment tree for the desired parent object.
    NOTE: This MUST be called at least once before "post_comment" or the root of the comment tree will not exist.
    """
    # TODO: Add the ability to return comment tree in JSON format.
    # First we get the root of the comment tree being requested
    tree_root, parent_object = _get_or_create_tree_root(request)

    # Check if the user doesn't pass the appropriate permission check (on the parent_object)...
    if not user_has_permission(request, parent_object, 'can_view_comments'):
        raise FailSafelyException("You do not have permission to view comments for this object.")

    # Once we have our desired nodes, we tack on all of the select/prefetch related stuff
    nodes = tree_root.get_family().select_related('deleted_user_info', 'created_by', 'parent', 'content_type')\
                                  .prefetch_related(Prefetch('versions', queryset=CommentVersion.objects.order_by('-date_posted')\
                                                                                                        .select_related('posting_user', 'deleted_user_info')))

    # The 'X_KWARGS' header is populated by settings.kwarg in comments.js
    kwargs = json.loads(request.headers.get('x-kwargs', {}))
    kwargs.update({
                   'nodes': nodes,
                   'parent_object': parent_object,
                   'max_depth': tree_root.max_depth
                   })

    comments_template = get_attr_val(request, parent_object, 'comments_template', 'comments/comments.html', **kwargs)

    # In the parent_object, sites can define a function called 'filter_nodes' if they wish to apply any additional filtering to the nodes queryset before it's rendered to the template.
    # Default value is the nodes tree with the deleted comments filtered out.
    nodes = get_attr_val(request, parent_object, "filter_nodes", default=nodes.filter(deleted=False), **kwargs)
    kwargs.update({"nodes": nodes, 'request': request})

    # Checks/assigns permissions to each node (so the template doesn't have to)
    _process_node_permissions(**kwargs)

    return JsonResponse({
        'ok': True,
        'html_content': loader.render_to_string(comments_template, context=kwargs, request=request),
        'number_of_comments': tree_root.get_descendant_count()
    })
