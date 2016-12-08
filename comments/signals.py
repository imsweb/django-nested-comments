from django.dispatch import Signal

# Sent when a comment is posted.
comment_posted = Signal(providing_args=('request', 'message'))