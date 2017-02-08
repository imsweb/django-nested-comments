from django.contrib.contenttypes.models import ContentType
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models

import json

class JSONField (models.TextField):
    """
        Temporary patch class until the minimum Django version is brought up to 1.9 (when the built in JSONField was introduced).
    """
    __metaclass__ = models.SubfieldBase

    def to_python(self, value):
        if value == '':
            return None
        if isinstance(value, basestring):
            return json.loads(value)
        return value

    def get_prep_value(self, value):
        if value == '':
            return None
        if isinstance(value, (dict, list, tuple)):
            return json.dumps(value, cls=DjangoJSONEncoder)
        return super(JSONField, self).get_prep_value(value)

    def value_to_string(self, obj):
        return self.get_prep_value(self._get_val_from_obj(obj))
    
class InvalidCommentException(Exception):
    """
    Throw this exception when a valid comment cannot be found/created based on the parameters of a request.
    """
    pass
    
def _get_target_comment(request):
    """
        Using parameters passed in with the request this function determines what the target comment is.
        This function returns the following tuple:
            (comment, version the user is editing (or None if new comment))
    """
    from .models import Comment, CommentVersion
    # Check if the user is attempting to edit an existing comment...
    if 'version_id' in request.POST:
        try:
            previous_version = CommentVersion.objects.select_related('comment').get(id=request.POST.get('version_id'))
            return previous_version.comment, previous_version
        except CommentVersion.DoesNotExist:
            raise InvalidCommentException("The comment you are attempting to update could not be found.")
    # Or they are trying to create a new comment...
    elif 'parent_id' in request.POST:
        try:
            parent = Comment.objects.get(id=request.POST.get('parent_id'))
            return Comment(parent=parent, created_by=request.user), None
        except Comment.DoesNotExist, e:
            raise InvalidCommentException("The comment you are responding to could not be found.")
    # Or we can't tell what they were trying to do, so we return a 404
    else:
        raise InvalidCommentException("An error occurred while saving your comment.")
    
def _get_or_create_tree_root(request):
    from .models import Comment
    if 'ct_id' in request.GET and 'obj_id' in request.GET:
        try:
            parent_comment = None
            ct = ContentType.objects.get_for_id(request.GET.get('ct_id'))
            obj_id = request.GET.get('obj_id')
            obj = ct.get_object_for_this_type(pk=obj_id)
            try:
                return Comment.objects.get(object_id=obj_id, content_type=ct), obj
            except Comment.DoesNotExist:
                kwargs = {}
                if hasattr(obj, 'max_comment_depth'):
                    kwargs['max_depth'] = getattr(obj, 'max_comment_depth')()
                # This 'lock' ensures the creation process is done serially, since there is a built in race condition for mptt's 'tree_id' assignment
                # The issue for mptt is here: https://github.com/django-mptt/django-mptt/issues/236
                ct_lock = ContentType.objects.select_for_update().get(app_label='comments', model='comment')
                comment = Comment.objects.create(content_object=obj, **kwargs)
                return comment, obj
        except Exception, e:
            raise InvalidCommentException("Unable to access comment tree: parent object not found.")
    else:
        raise InvalidCommentException("Unable to access comment tree: invalid request parameters.")
    
def get_attr_val(request, obj, attr, default=None, **kwargs):
    """
    This function attempts to get a value from the 'obj' through 'attr' (either a callable or a variable). 
    If 'attr' is not defined on 'obj' then we attempt to fall back to the default.
    """
    if hasattr(obj, attr):
        attr_holder = getattr(obj, attr)
        if callable(attr_holder):
            return attr_holder(request, **kwargs)
        return attr_holder
    return default
        
def user_has_permission(request, parent_object, permission_function, **kwargs):
    """
        Helper method that defaults all permission checks to "is_authenticated" if it is not defined on the parent_object.
    """
    default = request.user.is_authenticated()
    return get_attr_val(request, parent_object, permission_function, default, **kwargs)
