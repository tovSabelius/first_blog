from django.conf import settings
from django.db import models
from django.urls import reverse
from django.contrib.auth import get_user_model
from articles.utils import ru_slugify


class Note(models.Model):
    title = models.CharField(verbose_name="Заголовок", max_length=500, unique=True)
    author = models.CharField(verbose_name="Автор", max_length=200, default="Noname")
    text = models.TextField(verbose_name="Текст статьи", max_length=5000)
    date_publish = models.DateField(auto_now_add=True)
    slug = models.SlugField(
        verbose_name="Категория", max_length=150, unique=True, db_index=True
    )
    cat = models.ForeignKey("Category", on_delete=models.CASCADE, null=True)
    photo = models.ImageField(
        verbose_name="Фото к посту", upload_to="ALL_FILES/%Y/%m/%d", null=True
    )
    tags = models.ManyToManyField("TagNote", blank=True, related_name="tags")
    # Не каждая запись Note будет содержать тег. Чтобы допускать пустое поле в форме (сделать его необязательным), прописываем blank=True. Это относится к валидации формы.
    # При этом null=True относится к базе данных и говорит о том, что поле может принимать значение NULL, при этом это поле обязательное в формах.

    """
    Мы связали Note и TagNote с помощью ManyToManyField. Они связаны через промежуточную таблицу,
    которая связана с Note и TagNote с помощью ForeignKey, т.е. хранит в себе note_id и tagnote_id.
    related_name='tags' - это имя для обратного связывания тегов и соответствующих им записей. 
    Понадобится, когда мы будем искать записи, связанные с определённым тегом.
    
    Теперь, чтобы назначить теги нашим записям, заходим в shell и выбираем конкретную запись.
    Затем выбираем некоторое кол-во тегов и связываем выбранную запись с тегами с помощью
    <выбранная запись>.tags.set(<СПИСОК выбранных тегов>).
    Тег можно удалить с помощью <выбранная запись>.tags.remove(<переменная с ссылкой на тег>).
    Добавить отдельный тег: <выбранная запись>.tags.add(<переменная с ссылкой на тег>).
    Получить список всех тегов, привязанных к конкретной записи (и наоборот): <запись/тег>.tags.all()
    
    Затем я сделал несколько вещей:
    - Добавил представление show_tag_notelist, для отображение записей с определёнными тегами.
    - Сделал отображение всех тегов в сайдбаре через переменную all_tags
    - Сделал отображение тегов, связанных с конкретной записью при промотре конкретной записи через переменную related_tags
    """

    onetone = models.OneToOneField(
        "OneToOneModel",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="rels",
    )

    """
    Связали Note и OneToOneModel с помощью OneToOneField. Указали название related_name
    для обратного связывания.
    Назначил экземплярам Note экземпляры OneToOneField, предварительно создав их, через
    простое присваивание атрибуту onetone экземпляра OneToOneField.
    <экземпляр Note>.onetone = <экземпляр OneToOneField>
    <экземпляр OneToOneField>.rels = <экземпляр Note>. Или можно назначать экземпляры Note экземплярам OneToOneField.
    После любой из этих записей нужно прописать <экземпляр Note>.save(), т.к. произошли изменения в таблице Note.
    При этом мы не можем связать разные экземпляры Note с одним и тем же экземпляром OneToOneField.
    """
    user_note_connect = models.ForeignKey(
        get_user_model(), null=True, on_delete=models.CASCADE
    )
    likes = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name="like", blank=True
    )
    # Мн-во пользователей может иметь лайки, относящиеся к мно-ву постов.

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        categ = Category.objects.get(id=self.cat_id)
        return reverse(
            viewname="show_note",
            kwargs={"cat_slug": categ.slug, "note_slug": self.slug},
        )

    def save(self, *args, **kwargs):
        self.slug = ru_slugify(self.title)
        return super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Запись"
        verbose_name_plural = "Записи"


class Category(models.Model):
    cat_name = models.CharField(
        verbose_name="Название категории", unique=True, max_length=30
    )
    slug = models.SlugField(
        verbose_name="Слаг", max_length=255, unique=True, db_index=True
    )

    def __str__(self):
        return self.cat_name

    def get_absolute_url(self):
        return reverse(viewname="show_cat", kwargs={"cat_slug": self.slug})

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"


class FileModel(models.Model):
    file = models.FileField(verbose_name="Файл", upload_to="ALL_FILES/%Y/%m/%d")
    image = models.ImageField(
        verbose_name="Изображение", upload_to="ALL_FILES/%Y/%m/%d"
    )


class TagNote(models.Model):
    tagname = models.CharField(max_length=100, db_index=True)
    slug = models.SlugField(max_length=255, db_index=True, unique=True)

    def __str__(self):
        return self.tagname

    def get_absolute_url(self):
        return reverse(viewname="show_tag", kwargs={"tag_slug": self.slug})


class OneToOneModel(models.Model):
    name = models.CharField(max_length=100)
    age = models.IntegerField(null=True)

    def __str__(self):
        return self.name


class Comment(models.Model):
    author = models.CharField(verbose_name="Автор", max_length=200, default="Noname")
    text = models.TextField(verbose_name="Текст статьи", max_length=5000)
    note_connect = models.ForeignKey("Note", null=True, on_delete=models.CASCADE)
    user_connect = models.ForeignKey(
        get_user_model(), null=True, on_delete=models.CASCADE
    )
    date_create = models.DateField(auto_now_add=True, null=True)

    def __str__(self):
        return self.author
