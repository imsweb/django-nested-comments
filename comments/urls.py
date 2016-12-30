from django.conf.urls import patterns, url
from .views import load_comments

urlpatterns = patterns('comments.views',
   url(r'^load_comments/$', 'load_comments', name='load-comments'),
   url(r'^post_comment/$', 'post_comment', name='post-comment'),
   url(r'^delete_comment/$', 'delete_comment', name='delete-comment'),
)
