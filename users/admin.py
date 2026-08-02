from django.contrib import admin
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
# from users.models import User
from django.contrib.auth import get_user_model
 

admin.site.register(get_user_model(), UserAdmin)