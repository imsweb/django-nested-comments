from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from django.http.response import Http404
from django.shortcuts import render
from django.template import loader
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_GET

from .forms import CommentVersionForm
from .models import Comment, CommentVersion
from .utils import InvalidCommentException, _get_target_comment, _get_or_create_tree_root

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
    parent_object = comment.get_root().content_object
    if not user_has_permission(request, parent_object, 'post_comment', comment=comment):
        return JsonResponse({ 
            'ok': False,
            'error_message': "You do not have permission to post this comment.",
        })
    
    # If the comment object (NOT the message) hasn't been saved yet...
    if comment._state.adding == True:
        # TODO: Add the ability to override "position" (default is 'last-child')
        Comment.objects.insert_node(comment, parent_comment, save=True)
    
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
        version_form.save(commit=False)
        version_form.comment = comment
        version_form.posting_user = request.user
        new_version = version_form.save()
        return JsonResponse({ 
            'ok': True,
            date_posted: new_version.date_posted,
            posting_user: new_version.posting_user
        })
    else:
        return JsonResponse({ 
            'ok': False,
            'error_message': "There were errors in your submission. Please correct them and resubmit.",
            form_html: loader.render_to_string('comments/form.html', {'form': version_form})
        })
        
@require_GET
def view_comment(request):
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
            'html_content': loader.render_to_string('comments/comments.html', context={'nodes': root_comment.get_family(),}),
        })
    
    
    
        
    
    
        
        