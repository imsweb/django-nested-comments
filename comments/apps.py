from django.apps import AppConfig

class CommentsConfig (AppConfig):
    name = 'comments'

    RAISE_FAIL_SAFELY_EXCEPTION_ON_NEW_VERSION_FORM_FAILING = False

    def ready(self):
        pass

    def get_comment_version_form(self):
        from comments.forms import CommentVersionForm

        return CommentVersionForm
