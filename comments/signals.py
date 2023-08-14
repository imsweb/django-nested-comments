from django.dispatch import Signal

# The 'sender' will be the comment that changed
# 'kwargs' will contain the dictionary passed back from the ajax call in the 'X_KWARGS' header
#provides args 'comment', 'request', 'version_saved', 'comment_action', 'kwargs'
comment_changed = Signal()
