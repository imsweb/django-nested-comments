from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from django.http.response import Http404
from django.shortcuts import render
from django.template import loader
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from .forms import CommentVersionForm
from .models import Comment, CommentVersion

@transaction.atomic
@require_POST
def post_comment(request):
    # The user is attempting to edit an existing comment...
    existing_version = None
    if 'version_id' in request.POST:
        try:
            existing_version = CommentVersion.objects.get(id=request.POST.get('version_id')).select_related('comment')
            comment = comment_version.comment
        except CommentVersion.DoesNotExist:
            return JsonResponse({ 
                'ok': False,
                'error': "The comment you are attempting to update could not be found.",
            })
    # Or they are trying to create a new "sub" comment (a comment under a comment)...
    elif 'parent_id' in request.POST:
        try:
            parent_comment = Comment.object.get(id=request.POST.get('parent_id'))
            comment = Comment(parent_comment=parent_comment, created_by=request.user)
        except Comment.DoesNotExist:
            return JsonResponse({ 
                'ok': False,
                'error': "The comment you are responding to could not be found.",
            })
    # Or they are trying to create a new "top-level" comment...
    elif 'ct_id' in request.POST and 'obj_id' in request.POST:
        try:
            ct = ContentType.objects.get_for_id(request.POST.get('ct_id'))
            obj = ct.get_object_for_this_type(pk=request.POST.get('obj_id'))
            comment = Comment(content_object=obj, created_by=request.user)
        except:
            return JsonResponse({ 
                'ok': False,
                'error': "An error occurred while saving your comment.",
            })
    # Or we can't tell what they were trying to do, so we return a 404
    else:
        return JsonResponse({ 
            'ok': False,
            'error': "An error occurred while saving your comment.",
        })
    
    # Check if the user doesn't have the appropriate permissions...
    # TODO: Return a more explicit error
    if not user_has_permission(request, comment, 'post_comment'):
        return JsonResponse({ 
            'ok': False,
            'error': "You do not have permission to post this comment.",
        })
    
    # If the comment object (NOT the message) hasn't been saved yet...
    if comment._state.adding == True:
        comment.save()
    
    # Now that we have a comment object, we get a 'lock' on it to prevent a race condition
    try:
        Comment.objects.select_for_update(nowait=True).get(pk=comment.pk)
    except DatabaseError:
        # Someone is already trying to update this comment, so we need to return an appropriate error
        # TODO: Return a more specific error
        return JsonResponse({ 
            'ok': False,
            'error': "Someone else is currently editing this comment. Please refresh your page and try again.",
        })
    
    # Now we know we have sole access to the comment object at the moment so we need to check if we are editing the most recent version
    if existing_version and existing_version != comment.versions.latest():
        return JsonResponse({ 
            'ok': False,
            'error': "You are not editing the most recent version of this comment. Please refresh your page and try again.",
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
            'error': "There were errors in your submission. Please correct them and resubmit.",
            form_html: loader.render_to_string('comments/form.html', {'form': version_form})
        })
        
        