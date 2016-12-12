from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.db import models
from django.utils import timezone

from .utils import JSONField

class Comment (models.Model):
    parent_comment = models.ForeignKey('self', related_name="child_comments", null=True, blank=True)
    date_created = models.DateTimeField(default=timezone.now, editable=False)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='comments', null=True, blank=True)
    
    content_type = models.ForeignKey(ContentType, blank=True, null=True)
    object_id = models.PositiveIntegerField(blank=True, null=True)
    content_object = GenericForeignKey()
    
    # Use this to 'lock' the comment so two users do not edit the same comment at the same time
    transaction_lock = models.BooleanField(default=False)
    
    # User-defined data, stored as JSON in a text field.
    data = JSONField(null=True)
    
class CommentVersion (models.Model):
    comment = models.ForeignKey(Comment, related_name='versions')
    message = models.TextField()
    date_posted = models.DateTimeField(default=timezone.now, editable=False)
    posting_user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True)
    
    class Meta:
        get_latest_by = "date_posted"