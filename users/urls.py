from django.urls import path
from .views import *

app_name = 'users'

urlpatterns = [
    path('profile/edit-note/<int:pk>', edit_note, name='edit'),
    path('profile/delete/<int:pk>', delete_note, name='delete'),
    path('login/', LoginUser.as_view(), name='login'),
    path('logout/', log_out, name='logout'),
    path('register/', RegUser.as_view(), name='register'),
    path('profile/<int:pk>', user_profile, name='profile'),
    # path('profile/delete/<int:pk>', delete_note, name='delete'),
]