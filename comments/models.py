from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.db import models
from django.utils import timezone
from mptt.models import MPTTModel, TreeForeignKey

from .utils import JSONField

class Comment (MPTTModel):
    """
    This is the 'node' model of a comment tree.
    NOTE: The root object (the one with a content_object and no parent) is NOT a real comment, but allows for associating to any object.
    """
    parent = TreeForeignKey('self', null=True, blank=True, db_index=True)
    date_created = models.DateTimeField(default=timezone.now, editable=False)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='comments', null=True, blank=True)
    
    content_type = models.ForeignKey(ContentType, blank=True, null=True)
    object_id = models.PositiveIntegerField(blank=True, null=True)
    content_object = GenericForeignKey()
    
    # User-defined data, stored as JSON in a text field.
    data = JSONField(null=True)
    
    class MPTTMeta:
        order_insertion_by  = 'date_created'
    
class CommentVersion (models.Model):
    comment = models.ForeignKey(Comment, related_name='versions')
    message = models.TextField()
    date_posted = models.DateTimeField(default=timezone.now, editable=False)
    posting_user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True)
    
    class Meta:
        get_latest_by = "date_posted"