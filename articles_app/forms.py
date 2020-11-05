from .models import Comment
from django import forms


class CommentForm(forms.ModelForm):
    """A form for making a comment
    https://djangocentral.com/creating-comments-system-with-django/
    """
    class Meta:
        model = Comment
        fields = ('score', 'body')
