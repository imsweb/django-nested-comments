from django.dispatch import Signal

# The 'sender' will be the comment that changed
# 'kwargs' will contain the dictionary passed back from the ajax call in the 'X_KWARGS' header
comment_changed = Signal()
