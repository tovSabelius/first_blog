from .models import Category, TagNote


menu = ['О нас', 'Контакты', 'Партнёрство']
all_cats = Category.objects.all()
all_tags = TagNote.objects.all()


class DataMixin:
    def get_user_context(self, **kwargs):
        context = kwargs
        context.update({'menu': menu, 'all_cats': all_cats, 'title': 'Главная', 'all_tags': all_tags})
        
        if 'cat_selected' not in context:
            context['cat_selected'] = 0
        return context