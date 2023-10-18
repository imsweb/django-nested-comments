from django.urls import path
import comments.views as comment_views

urlpatterns = [
    path('load_comments/', comment_views.load_comments, name='load-comments'),
    path('post_comment/', comment_views.post_comment, name='post-comment'),
    path('delete_comment/', comment_views.delete_comment, name='delete-comment'),
]