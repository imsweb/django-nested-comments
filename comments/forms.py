from django import forms
from django.conf import settings

from .models import CommentVersion

import nh3

class CommentVersionForm(forms.ModelForm):
    class Meta:
        model = CommentVersion
        fields = ['message']
        
    def clean_message(self):
        message = self.cleaned_data['message']
        allowed_tags = settings.ALLOWED_TAGS if hasattr(settings, 'ALLOWED_TAGS') else nh3.ALLOWED_TAGS
        allowed_attributes = settings.ALLOWED_ATTRIBUTES if hasattr(settings, 'ALLOWED_ATTRIBUTES') else nh3.ALLOWED_ATTRIBUTES
        return nh3.clean(message, tags=allowed_tags, attributes=allowed_attributes, strip_comments=True, link_rel=None)