from django.urls import path
from .views import *
from django.conf import settings
from django.conf.urls.static import static
from users.views import DeleteNote

urlpatterns = [
    # path('<int:pk>', DeleteNote.as_view(), name='delete'),
    # path('', main, name='main'),
    path("like/<int:pk>", add_like, name="like_post"),
    path("comment/<slug:note_slug>", add_comment, name="co_post"),
    path("", Main.as_view(), name="main"),
    path("create/", create_note, name="create"),
    path("tags/<slug:tag_slug>", show_tag_notelist, name="show_tag"),
    path("send/", send_file, name="send"),
    path("<slug:cat_slug>/", ShowCat.as_view(), name="show_cat"),
    path("<slug:cat_slug>/<slug:note_slug>", ShowNote.as_view(), name="show_note"),
    # path('<int:pk>', create_comment, name='comment'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
# Добавляем в список маршрутов маршрут с префиксом MEDIA_URL, чтобы к ним можно было обратиться

print(str(static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)[0]))
print(repr(settings.MEDIA_URL))
