from django import forms
from django.conf import settings

from .models import CommentVersion

import nh3

class CommentVersionForm(forms.ModelForm):
    class Meta:
        model = CommentVersion
        fields = ['message']

    def __init__(self, *args, **kwargs):
        # Having this method accept kwargs but not passing kwargs into the super() call
        # is necessary because a child class may want to use kwargs in its __init__,
        # but if we pass into kwargs into super() here, a BaseModelForm.__init__()
        # got an unexpected keyword argument will happen.
        super().__init__(*args)

    def clean_message(self):
        message = self.cleaned_data['message']
        allowed_tags = settings.ALLOWED_TAGS if hasattr(settings, 'ALLOWED_TAGS') else nh3.ALLOWED_TAGS
        allowed_attributes = settings.ALLOWED_ATTRIBUTES if hasattr(settings, 'ALLOWED_ATTRIBUTES') else nh3.ALLOWED_ATTRIBUTES
        return nh3.clean(message, tags=allowed_tags, attributes=allowed_attributes, strip_comments=True, link_rel=None)