from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from django.http import JsonResponse
from django.http.response import Http404
from django.shortcuts import render
from django.template import loader
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_GET

from .forms import CommentVersionForm
from .models import Comment, CommentVersion
from .utils import InvalidCommentException, _get_target_comment, _get_or_create_tree_root, user_has_permission

@transaction.atomic
@require_POST
def post_comment(request):
    """
    View function that handles inserting new/editing previously existing comments
    """
    # Based on variables passed in we get the comment the user is attempting to create/edit
    try:
        comment, previous_version = _get_target_comment(request)
    except InvalidCommentException, e:
        return JsonResponse({ 
            'ok': False,
            'error_message': e.message,
        })
    
    # Check if the user doesn't pass the appropriate permission check (on the parent_object)...
    # We call this on the parent comment because the comment itself may not have been saved yet (can't call .get_root on it)
    parent_comment = comment.parent
    root_comment = parent_comment.get_root()
    parent_object = root_comment.content_object
    if not user_has_permission(request, parent_object, 'post_comment', comment=comment):
        return JsonResponse({ 
            'ok': False,
            'error_message': "You do not have permission to post this comment.",
        })
     
    # Check to make sure we are not trying to save a comment "deeper" than we are allowed...   
    if parent_comment.level >= root_comment.max_depth:
        return JsonResponse({ 
            'ok': False,
            'error_message': "You cannot respond this comment.",
        })
    
    # If the comment object (NOT the message) hasn't been saved yet...
    if comment._state.adding == True:
        # TODO: Add the ability to override "position" (default is 'last-child')
        comment = Comment.objects.insert_node(comment, parent_comment, save=True)
    
    # Now that we have a comment object, we get a 'lock' on it to prevent a race condition
    try:
        Comment.objects.select_for_update(nowait=True).get(pk=comment.pk)
    except DatabaseError:
        # Someone is already trying to update this comment, so we need to return an appropriate error
        return JsonResponse({ 
            'ok': False,
            'error_message': "Someone else is currently editing this comment. Please refresh your page and try again.",
        })
    
    # Now we know we have sole access to the comment object at the moment so we need to check if we are editing the most recent version
    if previous_version and previous_version != comment.versions.latest():
        return JsonResponse({ 
            'ok': False,
            'error_message': "You are not editing the most recent version of this comment. Please refresh your page and try again.",
        })
    
    # Everything has checked out, so we save the new version and return the appropriate response
    version_form = CommentVersionForm(request.POST)
    if version_form.is_valid():
        new_version = version_form.save(commit=False)
        new_version.comment = comment
        new_version.posting_user = request.user
        new_version.save()
        return JsonResponse({ 
            'ok': True,
        })
    else:
        return JsonResponse({ 
            'ok': False,
            'error_message': "There were errors in your submission. Please correct them and resubmit.",
            form_html: loader.render_to_string('comments/form.html', {'form': version_form})
        })
        
@transaction.atomic
@require_POST
def delete_comment(request):
    pass

@require_GET
def load_comments(request):
    """
    View function that returns the comment tree for the desired parent object.
    NOTE: This MUST be called at least once before "post_comment" or the root of the comment tree will not exist.
    """
    # TODO: Add the ability to return comment tree in JSON format.
    # First we get the root of the comment tree being requested
    try:
        root_comment = _get_or_create_tree_root(request)
    except InvalidCommentException, e:
        return JsonResponse({ 
            'ok': False,
            'error_message': e.message,
        })
        
    # Check if the user doesn't pass the appropriate permission check (on the parent_object)...
    if not user_has_permission(request, root_comment.content_object, 'view_comments'):
        return JsonResponse({ 
            'ok': False,
            'error_message': "You do not have permission to view comments for this object.",
        })
    
    return JsonResponse({ 
        'ok': True,
        'html_content': loader.render_to_string('comments/comments.html', context={'request': request, 'nodes': root_comment.get_family(),}),
    })
    
    
    
        
    
    
        
        