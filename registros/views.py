from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.http import HttpResponse
from django.http import JsonResponse
from django.db.models import Avg
import re
import json

from .models import Empresas, Usuários, Avaliações
# Create your views here.

def index(request):
    return render(request, "registros/index.html", {
        "empresas": Empresas.objects.all()
    })

def avaliacao(request, empresa_id):
    empresa = Empresas.objects.get(id=empresa_id)
    avaliacao = Avaliações.objects.filter(empresa_id=empresa_id)
    media = empresa.grade
    if media == -1:
        media = 'Sem avalições'
    return render(request, "registros/avaliacao.html", {
        "empresa": empresa,
        "avaliacoes": avaliacao,
        "media": media
    })

def registrar_usuario(request):
    if request.method == 'POST':
        erros = {}
        data = dict(request.POST)
        nome = data['nome'][0]
        email = data['email'][0]
        user = data['user-register'][0]
        senha = data['senha-register'][0]

        if len(nome) == 0:
            erros['nome'] = 'Inserir nome'
        elif len(nome) > 64:
            erros['nome'] = 'Nome muito grande'

        regex = '^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$'
        if not re.search(regex, email):
            erros['email'] = 'Email invalido'
        if len(email) > 64:
            erros['email'] = 'Email muito grande'
        
        if Usuários.objects.filter(user=user).count() != 0:
            erros['user-register'] = 'Usuario ja cadastrado'
        if len(user) > 64:
            erros['user-register'] = 'Nome de usuario muito grande'

        if len(senha) < 4 or len(senha)>64:
            erros['senha-register'] = 'A senha deve ter entre 5 e 64 caracteres'
        
        if len(erros.keys())>0:
            erros['ok'] = False
            return JsonResponse(erros)
        else:
            Usuários(name=nome, email = email, password = senha, user = user).save()
            request.session['username'] = user
            return JsonResponse({'ok': True, 'user':user})
    else:
        return JsonResponse({'erros':'metodo invalido'})

def entrar(request):
    if request.method == 'POST':
        erros = {}
        data = dict(request.POST)
        user = data['user-login'][0]
        senha = data['senha-login'][0]

        pw = Usuários.objects.filter(user=user).values('password')
        
        if pw.count() == 0:
            erros['user-login'] = 'Usuario nao encontrado'
        elif list(pw)[0]['password'] != senha:
            erros['senha-login'] = 'Senha incorreta'
        
        if len(erros.keys())>0:
            erros['ok'] = False
            return JsonResponse(erros)
        else:
            request.session['username'] = user
            return JsonResponse({'ok': True, 'user':user})
    else:
        return JsonResponse({'erros':'metodo invalido'})

def finalizar_sessao(request):
    request.session.pop('username', None)
    return JsonResponse({'ok':True})

def get_avaliacoes(request):
    user = None
    avaliacoes_arr = []

    if request.session.has_key('username'):
        user = request.session['username']
        userid = list(Usuários.objects.filter(user=user).values('id'))[0]['id']
        avaliacoes = Avaliações.objects.filter(user_id=userid)
        return render(request, "registros/minhas-avaliacoes.html", {"user" : user, "avaliacoes" : avaliacoes})
    else:
        return render(request, "registros/minhas-avaliacoes.html", {
            "message": "Você não possui avaliações"
        })

def obter_empresas(request):
    empresas = Empresas.objects.all()
    pontos = []
    for empresa in empresas:
        ponto = {}
        ponto['type'] = 'feature'
        ponto['geometry'] = {'type':'Point', 'coordinates':[empresa.longitude, empresa.latitude]}
        ponto['properties'] = {'title':empresa.name, 'description':empresa.address}
        pontos.append(ponto)
    return JsonResponse({'data':pontos})

def buscar_empresa(request):
    data = json.loads(request.body)
    lat = round(float(data['lat']), 4)
    longi = round(float(data['long']), 4)
    empresa = Empresas.objects.filter(longitude = longi, latitude = lat)
    if empresa.count() == 0:
        Empresas(address=data['endereco'], name = data['nome'], grade = -1, longitude = longi, latitude = lat).save()
        empresa = Empresas.objects.filter(longitude = longi, latitude = lat)
    return JsonResponse(dict(list(empresa.values())[0]))

def generate_avaliacao(request):
    data = dict(request.POST)
    comment = data['comentarios'][0]
    grade = data['nota'][0]
    empresa_id = data['id-empresa'][0]
    erros = {}

    if len(grade) == 0:
        erros['nota'] = 'Inserir nota'
        erros['ok'] = False
        return JsonResponse(erros)
    elif int(grade) > 10:
        erros['nota'] = 'Nota deve estar entre 0 e 10'
        erros['ok'] = False
        return JsonResponse(erros)
    elif int(grade) < 0:
        erros['nota'] = 'Nota deve estar entre 0 e 10'
        erros['ok'] = False
        return JsonResponse(erros)
        
    if len(comment) > 300:
        erros['comentario'] = 'Máximo de 300 caractéres'
        erros['ok'] = False
        return JsonResponse(erros)

    if request.method == 'POST':
        if request.session.has_key('username'):
            user = request.session['username']
            userid = list(Usuários.objects.filter(user=user).values('id'))[0]['id']
            empresa = Empresas.objects.get(id=empresa_id)
            Avaliações(comment=comment, grade=grade, empresa_id=empresa_id, user_id=userid, empresaname=empresa.name, username=user).save()
            media = Avaliações.objects.filter(empresa_id=empresa_id).aggregate(Avg('grade'))
            empresa.grade = round(media['grade__avg'])
            empresa.save()
            erros['ok'] = True
        else:
            erros['login'] = 'Você deve estar logado para fazer uma avaliação'
            erros['ok'] = False
        return JsonResponse(erros)
        
    else:
        return JsonResponse({'ok':False})