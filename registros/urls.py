from django.urls import path

from . import views
from home import views as homepage

urlpatterns = [
    path("", views.index, name="index"),
    path("home", homepage.index, name="home"),
    path("minhas-avaliacoes", views.get_avaliacoes),
    path("usuario/registrar", views.registrar_usuario),
    path("usuario/entrar", views.entrar),
    path("finalizarsessao", views.finalizar_sessao),
    path("<int:empresa_id>", views.avaliacao, name="avaliacao"),
    path("obter-empresas", views.obter_empresas),
    path("buscar-empresa", views.buscar_empresa),
    path("generate-avaliacao", views.generate_avaliacao)
]