from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from django.utils import timezone
from mptt.models import MPTTModel, TreeForeignKey


class DeletedUserInfo (models.Model):
    """
    This model stores basic information about a user when they are deleted.
    """
    first_name = models.TextField(blank=True)
    last_name = models.TextField(blank=True)
    email = models.TextField(blank=True)
    
class Comment (MPTTModel):
    """
    This is the 'node' model of a comment tree.
    NOTE: The root object (the one with a content_object and no parent) is NOT a real comment, but allows for associating to any object.
    """
    
    parent = TreeForeignKey('self', null=True, blank=True, db_index=True, on_delete=models.CASCADE)
    """ The parent comment, NULL if this is the root "comment" """
    
    date_created = models.DateTimeField(default=timezone.now, editable=False)
    """ The date the comment was created (defaults to timezone.now) """
    
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name='comments', null=True, blank=True)
    """ The User object (via FK to AUTH_USER_MODEL) that created this comment (originally) """
    
    deleted_user_info = models.ForeignKey(DeletedUserInfo, on_delete=models.SET_NULL, null=True, blank=True)
    """ If the user that created a comment is deleted, their information is associated here """
    
    max_depth = models.IntegerField(default=2)
    """ The maximum depth this comment tree can be (1 based), only really read from the root "comment" """
    
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, blank=True, null=True)
    object_id = models.PositiveIntegerField(blank=True, null=True)
    content_object = GenericForeignKey()
    
    data = models.JSONField(null=True)
    """ User-defined data, stored as JSON in a text field. """
    
    deleted = models.BooleanField(default=False)
    """ deleted flag if the comment was deleted by the user """
    
    class MPTTMeta:
        order_insertion_by  = 'date_created'
    
class CommentVersion (models.Model):
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='versions')
    message = models.TextField(blank=True)
    date_posted = models.DateTimeField(default=timezone.now, editable=False)
    posting_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    deleted_user_info = models.ForeignKey(DeletedUserInfo, on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        get_latest_by = "date_posted"
        
    
@receiver(pre_delete, sender=settings.AUTH_USER_MODEL)
def store_deleted_user(sender, **kwargs):
    instance = kwargs.get('instance', None)
    if instance:
        # TODO: Make this more generic? There is no guarantee that these values are applicable since we are using AUTH_USER_MODEL
        user_info = DeletedUserInfo.objects.get_or_create(first_name=getattr(instance, 'first_name', ''), last_name=getattr(instance, 'last_name', ''), email=getattr(instance, 'email', ''))[0]
        for comment in Comment.objects.filter(created_by=instance):
            comment.deleted_user_info = user_info
            comment.save()
        for comment_version in CommentVersion.objects.filter(posting_user=instance):
            comment_version.deleted_user_info = user_info
            comment_version.save()
        