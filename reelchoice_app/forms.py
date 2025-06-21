from django import forms

from .models import Comment


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'placeholder': 'Write your comment',
                'rows': 3,
                'class': 'w-full p-4 bg-[#2a2a2a] text-white rounded-lg resize-none focus:outline-none focus:ring-2 focus:ring-gray-500'
            })
        }