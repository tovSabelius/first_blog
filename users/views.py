from django.urls import reverse, reverse_lazy
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.contrib.auth import authenticate, login, logout
from .forms import *
from articles.models import Category, TagNote, Note
from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic import CreateView
from articles.mixins import DataMixin
from django.views.generic import DeleteView
from django.shortcuts import get_object_or_404
from django.conf import settings


menu = ['О нас', 'Контакты', 'Партнёрство']
all_cats = Category.objects.all()
all_tags = TagNote.objects.all()


# def log_in(request):
#     if request.method == 'POST':
#         form = LoginForm(request.POST)
#         if form.is_valid():
#             cd = form.cleaned_data
#             user = authenticate(request, username=cd['username'], password=cd['password'])
#             if user is not None and user.is_active:
#                 login(request, user)
#                 return redirect(reverse_lazy('main'))
#     else:
#         form = LoginForm()
#     return render(request, 'users/login.html', context={'form': form,
#                                 'all_cats': all_cats, 'menu': menu, 'title': 'Авторизация'})

class LoginUser(DataMixin, LoginView):
    template_name = 'users/login.html'
    form_class = LoginForm

    def get_success_url(self):
        return reverse_lazy('main')
    
    def get_context_data(self, **kwargs):
        context = self.get_user_context(**kwargs)
        context['cat_selected'] = None
        context.update(super().get_context_data(**kwargs))
        return context


def log_out(request):
    logout(request)
    return redirect(reverse('users:login'))


# def register(request):
#     if request.method == 'POST':
#         form = RegForm(request.POST)
#         if form.is_valid():
#             cd = form.cleaned_data
#             user = form.save(commit=False)
#             user.set_password(cd['password'])
#             user.save()
#             login(request, user)
#             return redirect(reverse_lazy('main'))
#     else:
#         form = RegForm()
#     return render(request, 'users/register.html', context={'form': form,
#                                 'all_cats': all_cats, 'menu': menu, 'title': 'Регистрация'})


class RegUser(DataMixin, CreateView):
    template_name = 'users/register.html'
    form_class = RegForm
    model = get_user_model()

    def get_success_url(self):
        return reverse_lazy('main')
    
    def get_context_data(self, **kwargs):
        context = self.get_user_context(**kwargs)
        context['cat_selected'] = None
        context.update(super().get_context_data(**kwargs))
        return context


def user_profile(request, pk):
    user = request.user
    notes = user.note_set.all()
    form = ProfileForm(instance=user)
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=user) # Обязательно указывай параметр instance!
        if form.is_valid():
            form.save()
            return redirect(reverse('main'))
        
    context = {'all_cats': all_cats, 'menu': menu, 
               'all_tags': all_tags, 'notes': notes, 
               'form': form, 'default_avatar': settings.DEFAULT_USER_IMAGE}
    return render(request, 'users/profile.html', context=context)



class DeleteNote(DataMixin, DeleteView):
    model = Note
    template_name = 'users/delete.html'
    extra_context = {'all_cats': all_cats, 'menu': menu, 
               'all_tags': all_tags,}
    success_url = reverse_lazy('main')
    
    
def delete_note(request, pk):
    note = Note.objects.get(pk=pk)
    context = {'all_cats': all_cats, 'menu': menu, 
               'all_tags': all_tags}
    if request.method == 'POST':
        note.delete()
        return redirect(reverse('users:profile', kwargs={'pk': request.user.id}))
    return render(request, 'users/delete.html', context=context)


def edit_note(request, pk):
    note = Note.objects.get(pk=pk)
    form = EditForm(instance=note)
    context = {'all_cats': all_cats, 'menu': menu, 
               'all_tags': all_tags, 'form': form,
               'title': f'Изменить {note.title}'}
    if request.method == 'POST':
        form = EditForm(request.POST, request.FILES, instance=note)
        if form.is_valid():
            form.save()
        return redirect(reverse('users:profile', kwargs={'pk': request.user.id}))
    return render(request, 'users/edit.html', context=context)
