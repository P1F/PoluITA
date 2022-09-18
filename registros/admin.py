from django.contrib import admin

# Register your models here.

from .models import Empresas, Avaliações, Usuários

admin.site.register(Empresas)
admin.site.register(Avaliações)
admin.site.register(Usuários)