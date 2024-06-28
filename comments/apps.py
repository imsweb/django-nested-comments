from django.apps import AppConfig

class CommentsConfig (AppConfig):
    name = 'comments'

    RAISE_EXCEPTION_ON_VERSION_FAIL = True
    # This variable is used when the CommentVersionForm is invalid.
    # When true, an exception will be raised.
    # When false, the errors from the form will be passed into the error_message
    # in the JavaScript, and that message will be displayed to the user.

    def ready(self):
        pass

    def get_comment_version_form(self):
        from comments.forms import CommentVersionForm

        return CommentVersionForm
