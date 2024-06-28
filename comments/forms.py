from django import forms
from django.conf import settings
from django.forms.utils import ErrorList

from .models import CommentVersion

import nh3

class CommentVersionForm(forms.ModelForm):
    class Meta:
        model = CommentVersion
        fields = ['message']

    def __init__(
        self,
        data=None,
        files=None,
        auto_id="id_%s",
        prefix=None,
        initial=None,
        error_class=ErrorList,
        label_suffix=None,
        empty_permitted=False,
        instance=None,
        use_required_attribute=None,
        renderer=None,
        **kwargs,
    ):
        for k, v in kwargs.items():
            setattr(self, k, v)
        super().__init__(data, files, auto_id, prefix, initial, error_class, label_suffix, empty_permitted, instance, use_required_attribute, renderer)

    def clean_message(self):
        message = self.cleaned_data['message']
        allowed_tags = settings.ALLOWED_TAGS if hasattr(settings, 'ALLOWED_TAGS') else nh3.ALLOWED_TAGS
        allowed_attributes = settings.ALLOWED_ATTRIBUTES if hasattr(settings, 'ALLOWED_ATTRIBUTES') else nh3.ALLOWED_ATTRIBUTES
        return nh3.clean(message, tags=allowed_tags, attributes=allowed_attributes, strip_comments=True, link_rel=None)