from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth import get_user_model
from articles.models import Category, Note


# class LoginForm(forms.Form):
#     username = forms.CharField(label='Логин', max_length=30, required=True, widget=forms.TextInput(attrs={'class': 'form-input'}))
#     password = forms.CharField(label='Пароль', widget=forms.PasswordInput(attrs={'class': 'form-input'}), required=True)


class LoginForm(AuthenticationForm):
    username = forms.CharField(label='Логин', max_length=30, required=True, widget=forms.TextInput(attrs={'class': 'form-input'}))
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput(attrs={'class': 'form-input'}), required=True)

    class Meta:
        model = get_user_model()
        fields = ('username', 'password')



class RegForm(UserCreationForm):
    username = forms.CharField(label='Логин', max_length=30, required=True, widget=forms.TextInput(attrs={'class': 'form-input'}))
    password1 = forms.CharField(label='Пароль', required=True, max_length=30, widget=forms.PasswordInput(attrs={'class': 'form-input'}))
    password2 = forms.CharField(label='Повтори пароль', required=True, max_length=30, widget=forms.PasswordInput(attrs={'class': 'form-input'}))
    
    def clean_password2(self):
        cd = self.cleaned_data
        if cd['password2'] == cd['password1']:
            return cd['password2']
        raise forms.ValidationError('Пароли не совпадают!!!')


    class Meta:
        model = get_user_model()
        fields = ('username', 'date_birth', 'password1', 'password2')
        widgets = {
            'date_birth': forms.SelectDateWidget(attrs={'class': 'form-input'})
        }
    

class ProfileForm(forms.ModelForm):

    class Meta:
        model = get_user_model()
        fields = ['username', 'avatar']

        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-input'}),
            'avatar': forms.FileInput(attrs={'class': 'form-file-input'}),
            'date_birth': forms.SelectDateWidget(attrs={'class': 'form-input'}),
            'password': forms.PasswordInput(attrs={'class': 'form-input'})
        }


class EditForm(forms.ModelForm):
    cat = forms.ModelChoiceField(queryset=Category.objects.all(), empty_label='Категория не выбрана', label='Категория')
    class Meta:
        model = Note
        fields = ['title', 'text', 'photo', 'cat', 'tags', 'onetone']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-input'}),
            'author': forms.TextInput(attrs={'class': 'form-input'}),
            'text': forms.Textarea(attrs={'class': 'form-input'}),
            'slug': forms.TextInput(attrs={'class': 'form-input'}),
            'photo': forms.FileInput(attrs={'class': 'form-file-input'}),
            'tags': forms.CheckboxSelectMultiple(),
        }

        labels = {
            'slug': 'URL',
            'photo': "Фото к посту",
            'tags': 'Теги',
        }