from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from .forms import *
from .models import *
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DetailView, ListView, CreateView
from .mixins import DataMixin
import os
import uuid
from django.db.models import Q


menu = ["О нас", "Контакты", "Партнёрство"]
all_cats = Category.objects.all()
all_tags = TagNote.objects.all()


# def main(request):
#     notes = Note.objects.all()
#     context = {'title': 'Главная', 'notes': notes,
#                'menu': menu, 'all_cats': all_cats, 'cat_selected': 0}
#     return render(request, 'articles/main.html', context)


class Main(DataMixin, ListView):
    model = Note
    template_name = "articles/main.html"
    context_object_name = "notes"

    def get(self, request):
        """
        Проверяем таким образом сделан запрос или нет. Если нет, значит поиска не происходило и нужно отобразить все посты.
        Для этого нужно сделать заглушку в виде пустой строки. Это позволит пройти фильтрацию.
        Ведь любая строка содержит пустую строку, таким образом проверка на содержание пустой строки
        выдаст посты.
        """
        query = request.GET.get("query") if request.GET.get("query") != None else ""
        context = self.get_user_context()
        if query:
            context["cat_selected"] = None
        context["search_form"] = SearchForm()
        context["notes"] = Note.objects.filter(
            Q(title__icontains=query) | Q(text__icontains=query)
        )
        return render(request, self.template_name, context=context)

    def get_context_data(self, **kwargs):
        context = self.get_user_context(**kwargs)
        context.update(super().get_context_data(**kwargs))

        # context['title'] = 'Главная'
        # context['menu'] = menu
        # context['all_cats'] = all_cats
        # context['cat_selected'] = 0
        return context

    def get_queryset(self):
        return Note.objects.all()


# @login_required(login_url='users:login')
# def show_note(request, cat_slug, note_slug):
#     note = get_object_or_404(Note, slug=note_slug)
#     context = {'note': note, 'menu': menu, 'all_cats': all_cats}
#     return render(request, 'articles/note.html', context)


class ShowNote(LoginRequiredMixin, DataMixin, DetailView):
    model = Note
    template_name = "articles/note.html"
    context_object_name = "note"
    login_url = "users:login"
    slug_url_kwarg = "note_slug"
    comment_form = CommentForm()

    def get_context_data(self, **kwargs):
        context = self.get_user_context(**kwargs)
        context.update(super().get_context_data(**kwargs))
        context["comments"] = Comment.objects.filter(note_connect_id=context["note"].id)
        context["form"] = self.comment_form
        context["cat_selected"] = None
        context["likes"] = context["note"].likes.count()
        liked = False
        if context["note"].likes.filter(pk=self.request.user.id).exists():
            liked = True
        context["liked"] = liked  # Эта переменная нам понадобится в шаблоне, чтобы
        # проверить лайкнул пользователь или дизлайкнул. Если лайкнул, мы будем
        # отображать кнопку дизлайка, если дизлайкнул (нажал кнопку лайка повторно),
        # будем отображать кнопку лайка.

        # context = super().get_context_data(**kwargs)
        # context.update({'menu': menu, 'all_cats': all_cats})
        return context

    def post(self, request, **kwargs):
        if request.POST.get("like-button") is not None:
            note = get_object_or_404(Note, pk=request.POST.get("like-button"))
            if note.likes.filter(pk=request.user.id).exists():
                note.likes.remove(request.user)
            else:
                note.likes.add(request.user)
            return redirect(note.get_absolute_url())

        else:
            note = Note.objects.get(slug=kwargs["note_slug"])
            form = CommentForm(request.POST)
            if form.is_valid():
                comment = form.save(commit=False)
                comment.author = self.request.user.username
                comment.note_connect_id = note.pk
                comment.user_connect_id = self.request.user.pk
                comment.save()
            return redirect(note.get_absolute_url())


def add_comment(request, note_slug):
    note = get_object_or_404(Note, slug=note_slug)
    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user.username
        comment.note_connect_id = note.pk
        comment.user_connect_id = request.user.pk
        comment.save()
    return redirect(note.get_absolute_url())


def add_like(request, pk):
    note = get_object_or_404(Note, pk=pk)
    if note.likes.filter(
        pk=request.user.id
    ).exists():  # Если пользователь уже лайкал пост
        note.likes.remove(
            request.user
        )  # И нажимает на эту кнопку снова, значит это означает дизлайк.
        # А значит лайк нужно удалить, т.е. мы из списка пользователей удаляем того,
        # кто нажал кнопку лайка повторно.
    else:
        note.likes.add(request.user)
    return redirect(note.get_absolute_url())


"""
Я добавил возможность добавления комментариев, а также лайков и дизлайков на странице
отображения конкретной записи. Таким образом, у меня может быть как бы 2 вида post-запроса:
1. Юзер лайкнул или дизлайкнул.
2. Юзер отправил комментарий.
Тогда нам нужно две формы и нужна возможность обрабатывать несколько пост-запросов
с одно страницы. По сути тут есть два выхода.
1. Запросы обрабатывают несколько разных представлений. Причём не только post-запросы,
но и get тоже. 1ая вьюха отображает конкретную запись, 2ая пишет комментарии, 3яя (диз)лайкает.
Для этого в каждой из форм, соответствующих определённому типу post-запроса, нужно прописать
url вьюхи в атрибуте action, которая будет обрабатывать данные из этой формы.
Например в форме, где (диз)лайкают, нужно прописать action='{% url 'like_post' note.pk %}'.
По умолчанию action='', что значит, что данные формы обрабатывает та же вьюха, что и отображала
конкретную запись. Этот способ будет следующим
2. Все запросы обрабатывает единственная вьюха. Тогда у форм НЕ надо прописывать
action, т.к. все запросы с этой страницы будет обрабатывать та же вьюха, что и отображала
эту страницу. Но тогда в одном из полей каждой из форм (или в нескольких формах, в зависимости от того, сколько post-запр. мы делаем со страницы)
надо прописать имя (name) и value - по сути, любое тестовое значение, например id текущего поста
(но можно и любое другое число). Тогда во время post-запр. в словаре request.POST будет
элемент с ключом name и значением value. И мы будем проверять с помощью request.POST.get(name),
если во время какого-то post-запр. это значение равно None или атрибуту value поля.
Если равно None, значит в словаре вообще нет ключа с именем name, а значит мы не обрабатываем
форму, которой принадлежит это поле по имени name. Значит, мы обрабатываем другую форму и ту же
самую проверку надо провернуть с ней.
Именно эта логика у меня прописана в методе post представления ShowNote.
* Вьюхи add_comment и add_like я оставил для примера, они рабочие и маршруты для них прописаны,
но они нигде не используются.
"""

# def show_cat(request, cat_slug):
#     chosen_cat = Category.objects.get(slug=cat_slug)
#     notes = Note.objects.filter(cat_id=chosen_cat.id)
#     context = {'title': 'Главная', 'notes': notes, 'all_cats': all_cats,
#                'menu': menu, 'cat_selected': chosen_cat.id}
#     return render(request, 'articles/main.html', context)


class ShowCat(DataMixin, ListView):
    model = Category
    template_name = "articles/main.html"
    context_object_name = "notes"
    allow_empty = False

    def get_context_data(self, **kwargs):
        context = self.get_user_context(**kwargs)
        context.update(super().get_context_data(**kwargs))
        # context = super().get_context_data(**kwargs)
        # context['title'] = 'Главная'
        # context['menu'] = menu
        # context['all_cats'] = all_cats
        context["cat_selected"] = context["notes"][0].cat_id
        context["search_form"] = SearchForm()
        return context

    def get_queryset(self):
        return Note.objects.filter(cat__slug=self.kwargs["cat_slug"])


@login_required(login_url="users:login")
def create_note(request):
    if request.method == "POST":
        form = NoteForm(request.POST, request.FILES)
        if form.is_valid():
            # cd = form.cleaned_data
            # Note.objects.create(**cd)
            note = form.save(commit=False)
            note.author = request.user.username
            note.user_note_connect_id = request.user.pk
            note.save()
            note.tags.set(form.cleaned_data["tags"])
            print(
                form.cleaned_data["tags"]
            )  # <QuerySet [<TagNote: Бэкенд>, <TagNote: Фронтенд>, <TagNote: Девопс>]>
            # Важно!!! Сначала надо сохранить запись, чтобы у неё появился id, а уже
            # потом добавлять значения M2M Field.
            # Вот ошибка: ValueError: "<Note: какое-то имя>" needs to have a value for field "id" before this many-to-many relationship can be used.
            return redirect(reverse("main"))
    else:
        form = NoteForm()
    context = {
        "title": "Создать статью",
        "all_cats": all_cats,
        "menu": menu,
        "form": form,
        "all_tags": all_tags,
    }
    return render(request, "articles/create.html", context)


"""
Помни!!!
* Во время отправки файлов на сервер нужно во время создания формы указывать
не только request.POST, но и request.FILES.
* В моделях обязательно нужно указывать upload_to.
* В шаблоне в форме дожен быть атрибут enctype="multipart/form-data", иначе ничего не сработает!!!
* В settings.py прописывай переменную media!!!
"""

# class CreateNote(LoginRequiredMixin, DataMixin, CreateView):
#     model = Note
#     template_name = 'articles/create.html'
#     form_class = NoteForm
#     login_url = 'users:login'

#     def get_context_data(self, **kwargs):
#         context = self.get_user_context(**kwargs)
#         context.update(super().get_context_data(**kwargs))
#         context['title'] = 'Создать статью'
#         return context


def handle_uploaded_file(file):
    n = file.name
    first = n[: n.rindex(".")]
    second = n[n.rindex(".") :]
    # if file.name in os.listdir('UPLOADS'):
    #     file.name = first + str(os.listdir('UPLOADS').count(file.name)) + second
    file.name = (
        first + str(uuid.uuid4()) + second
    )  # Предусматриваем, если загружаюься файлы с одинаковым именем
    with open(
        f"UPLOADS/{file.name}", "wb"
    ) as destination:  # Директорию UPLOADS нужно сначала создать
        for chunk in file.chunks():
            destination.write(chunk)


def send_file(request):
    if request.method == "POST":
        # handle_uploaded_file(request.FILES['file_upload'])
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            # handle_uploaded_file(form.cleaned_data['file']) Теперь используем форму, связанную с моделью и нам эта функция не нужна
            form.save()
    else:
        form = UploadFileForm()
    return render(request, "articles/send_f.html", {"form": form})


def show_tag_notelist(request, tag_slug):
    tag = get_object_or_404(TagNote, slug=tag_slug)
    notes = tag.tags.all()  # tags - это имя из related_name='tags' в модели.
    context = {
        "note_tags": notes,
        "title": tag.tagname,
        "menu": menu,
        "all_cats": all_cats,
        "all_tags": all_tags,
        "cat_selected": None,
        "search_form": SearchForm(),
    }

    return render(request, "articles/main.html", context=context)
    # for note in Note.objects.all():
    #     if tag in note.tags.all():


# context['search_form'] = SearchForm()
