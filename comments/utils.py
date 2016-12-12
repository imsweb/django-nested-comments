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
    
def user_has_permission(request, comment, permission_function):
    """
        Allows the associated object to define its own permission functions.
        If permission_function is not defined we fall back to 'is_authenticated()'.
    """
    obj = comment.content_object
    auth = request.user.is_authenticated()
    if hasattr(obj, permission_function):
        auth = getattr(obj, permission_function)(request, comment)
    return auth