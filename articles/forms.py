from dataclasses import fields
from django import forms
from .models import *
from string import ascii_lowercase


# class NoteForm(forms.Form):
#     title = forms.CharField(max_length=50, label='Заголовок', widget=forms.TextInput(attrs={'class': 'form-input'}))
#     author = forms.CharField(max_length=50, label='Автор', widget=forms.TextInput(attrs={'class': 'form-input'}))
#     text = forms.CharField(label='Текст', widget=forms.Textarea(attrs={'class': 'form-input'}))
#     date_publish = forms.DateField(label='Дата пубикации', widget=forms.DateInput(attrs={'class': 'form-input'}))
#     slug = forms.CharField(max_length=50, label='Категория', widget=forms.TextInput(attrs={'class': 'form-input'}))

class NoteForm(forms.ModelForm):
    cat = forms.ModelChoiceField(queryset=Category.objects.all(), empty_label='Категория не выбрана', label='Категория')
    class Meta:
        model = Note
        fields = ['title', 'text', 'photo', 'cat', 'tags', 'onetone']
        
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-input'}),
            'author': forms.TextInput(attrs={'class': 'form-input'}),
            'text': forms.Textarea(attrs={'class': 'form-input'}),
            'slug': forms.TextInput(attrs={'class': 'form-input'}),
            'tags': forms.CheckboxSelectMultiple(),
        }

        labels = {
            'slug': 'URL',
            'photo': "Фото к посту",
            'tags': 'Теги',
        }

'''
Короче, главное отличие просто форм от форм, связанных с моделями в том, что
в первом случае ты сам прописываешь поля, а во втором отображаешь поля, прописанные в модели,
указывая при этом, для какой модели ты это делаешь и из каких полей берёшь инфу в классе Meta.
Также обычная форма не имеет метода save, в то время как форма для модели имеет.
И результатом работы этого метода является ссылка на экземпляр модели и имеет все атрибуты,
прописанные в модели.
'''


# class UploadFileForm(forms.Form):
#     file = forms.FileField(label='Файл')


class UploadFileForm(forms.ModelForm):
    class Meta:
        model = FileModel
        fields = ('file', 'image')


class CommentForm(forms.ModelForm):
    # note_connect = forms.ModelChoiceField(queryset=Note.objects.all(), )
    class Meta:
        model = Comment
        fields = ['text']

        widgets = {
            'author': forms.TextInput(attrs={'class': 'form-input'}),
            'text': forms.Textarea(attrs={'class': 'form-input'})
        }

        labels = {
            'text': 'Оставьте комментарий!'
        }

class SearchForm(forms.Form):
    query = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Найти'}))
