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
    # Check if the user is attempting to edit an existing comment...
    if 'version_id' in request.POST:
        try:
            previous_version = CommentVersion.objects.get(id=request.POST.get('version_id')).select_related('comment')
            return previous_version.comment, previous_version
        except CommentVersion.DoesNotExist:
            raise InvalidCommentException("The comment you are attempting to update could not be found.")
    # Or they are trying to create a new comment...
    elif 'parent_id' in request.POST:
        try:
            parent_comment = Comment.object.get(id=request.POST.get('parent_id'))
            return Comment(parent_comment=parent_comment, created_by=request.user), None
        except Comment.DoesNotExist:
            raise InvalidCommentException("The comment you are responding to could not be found.")
    # Or we can't tell what they were trying to do, so we return a 404
    else:
        raise InvalidCommentException("An error occurred while saving your comment.")
    
def _get_or_create_tree_root(request):
    if 'ct_id' in request.GET and 'obj_id' in request.GET:
        try:
            parent_comment = None
            ct = ContentType.objects.get_for_id(request.GET.get('ct_id'))
            obj = ct.get_object_for_this_type(pk=request.GET.get('obj_id'))
            return Comment.objects.get_or_create(content_object=obj)
        except:
            raise InvalidCommentException("Unable to access comment tree: parent object not found.")
    else:
        raise InvalidCommentException("Unable to access comment tree: invalid request parameters.")
        
def user_has_permission(request, parent_object, permission_function, **kwargs):
    """
        Allows the associated object to define its own permission functions.
        If permission_function is not defined we fall back to 'is_authenticated()'.
        NOTE: kwargs can pass any necessary objects to the permission function and will vary based on what permission we are checking.
    """
    auth = request.user.is_authenticated()
    if hasattr(parent_object, permission_function):
        auth = getattr(parent_object, permission_function)(request, **kwargs)
    return auth