from django.conf.urls import url
import comments.views as comment_views

urlpatterns = [
    url(r'^load_comments/$', comment_views.load_comments, name='load-comments'),
    url(r'^post_comment/$', comment_views.post_comment, name='post-comment'),
    url(r'^delete_comment/$', comment_views.delete_comment, name='delete-comment'),
]