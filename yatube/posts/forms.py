from django import forms

from .models import Comment, Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('text', 'group', 'image')
        help_texts = {
            'text': 'Текст нового поста',
            'group': 'Группа, к которой будет относиться пост',
        }
        widgets = {
            'text': forms.Textarea(
                attrs={'placeholder': 'Ввести текст поста здесь ...'}
            ),
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text', )
        widgets = {
            'text': forms.Textarea(
                attrs={'placeholder': 'Ввести текст комментария здесь ...'}
            )
        }
