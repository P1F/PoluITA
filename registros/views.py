from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.http import HttpResponse
from django.http import JsonResponse
from django.db.models import Avg
import aqi
import re
import json
from datetime import datetime, timezone

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
        isSuperUser = user == 'admin'

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
            Usuários(name=nome, email = email, password = senha, user = user, super = isSuperUser).save()
            request.session['username'] = user
            request.session['isSuperUser'] = isSuperUser
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
            isSuperUser = Usuários.objects.get(user=user).super
            request.session['username'] = user
            request.session['isSuperUser'] = isSuperUser
            return JsonResponse({'ok': True, 'user':user})
    else:
        return JsonResponse({'erros':'metodo invalido'})

def finalizar_sessao(request):
    request.session.pop('username', None)
    request.session.pop('isSuperUser', None)
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
        ponto['properties'] = {'title':empresa.name, 'last_updated': empresa.last_updated.strftime('%Y-%m-%d %H:%M:%S %Z'), 'nota':empresa.grade, 'description':empresa.address, 'pm25': empresa.pm25, 'pm10': empresa.pm10, 'co': empresa.co, 'co2': empresa.co2, 'ch4': empresa.ch4, 'lpg': empresa.lpg, 'humidade': empresa.humidity, 'temperatura': empresa.temperature}
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
    pm25 = data['pm25'][0]
    pm10 = data['pm10'][0]
    co = data['co'][0]
    co2 = data['co2'][0]
    lpg = data['lpg'][0]
    ch4 = data['ch4'][0]
    humidity = data['umidade'][0]
    temperature = data['temperatura'][0]
    empresa_id = data['id-empresa'][0]
    erros = {}

    if len(pm25) <= 0:
        erros['pm25'] = 'PM2.5 deve ser maior que 0'
        erros['ok'] = False
        return JsonResponse(erros)

    if len(pm10) <= 0:
        erros['pm10'] = 'PM10 deve ser maior que 0'
        erros['ok'] = False
        return JsonResponse(erros)
    
    if len(co) <= 0:
        erros['co'] = 'CO deve ser maior que 0'
        erros['ok'] = False
        return JsonResponse(erros)

    if len(co2) <= 0:
        erros['co2'] = 'CO2 deve ser maior que 0'
        erros['ok'] = False
        return JsonResponse(erros)

    if len(lpg) <= 0:
        erros['lpg'] = 'LPG deve ser maior que 0'
        erros['ok'] = False
        return JsonResponse(erros)

    if len(ch4) <= 0:
        erros['ch4'] = 'CH4 deve ser maior que 0'
        erros['ok'] = False
        return JsonResponse(erros)

    if len(humidity) <= 0:
        erros['umidade'] = 'Umidade deve ser maior que 0'
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
            empresa.pm25 = aqi.to_aqi([
    (aqi.POLLUTANT_PM25, pm25)])
            empresa.pm10 = aqi.to_aqi([
    (aqi.POLLUTANT_PM10, pm10)])
            empresa.co = aqi.to_aqi([
    (aqi.POLLUTANT_CO_8H, co)])
            empresa.co2 = co2
            empresa.lpg = lpg
            empresa.ch4 = ch4
            empresa.humidity = humidity
            empresa.temperature = temperature
            empresa.last_updated = datetime.now(timezone.utc)
            empresa.grade = aqi.to_aqi([
    (aqi.POLLUTANT_PM25, pm25),
    (aqi.POLLUTANT_PM10, pm10),
    (aqi.POLLUTANT_CO_8H, co)
])
            Avaliações(comment=comment, grade=empresa.grade, pm25=pm25, pm10=pm10, co=co, co2=co2, lpg=lpg, ch4=ch4, humidity=humidity, temperature=temperature,
                empresa_id=empresa_id, user_id=userid, empresaname=empresa.name, username=user).save()
            media = Avaliações.objects.filter(empresa_id=empresa_id).aggregate(Avg('grade'))
            empresa.save()
            erros['ok'] = True
        else:
            erros['login'] = 'Você deve estar logado para fazer uma avaliação'
            erros['ok'] = False
        return JsonResponse(erros)
        
    else:
        return JsonResponse({'ok':False})


def insert_rating(request):
    data = dict(request.POST)
    comment = data['comentarios'][0]
    pm25_raw = data['pm25'][0]
    pm10_raw = data['pm10'][0]
    co_raw = data['co'][0]
    pm25 = aqi.to_aqi([(aqi.POLLUTANT_PM25, pm25_raw)])
    pm10 = aqi.to_aqi([(aqi.POLLUTANT_PM10, pm10_raw)])
    co = aqi.to_aqi([(aqi.POLLUTANT_CO_8H, co_raw)])
    grade = max(pm25, pm10, co)
    co2 = data['co2'][0]
    lpg = data['lpg'][0]
    ch4 = data['ch4'][0]
    humidity = data['umidade'][0]
    temperature = data['temperatura'][0]
    empresa_id = data['id-empresa'][0]
      # TODO: Add support to get company by address
      # lat = round(float(data['lat'][0]), 4)
      # longi = round(float(data['long'][0]), 4)
      # empresa = Empresas.objects.filter(longitude = longi, latitude = lat)
      # if empresa.count() == 0:
      #     Empresas(address=data['endereco'], name = data['nome'], grade = -1, longitude = longi, latitude = lat).save()
      #     empresa = Empresas.objects.filter(longitude = longi, latitude = lat)
      #     empresa_id = empresa.id
  
    username = data['username'][0]
    erros = {}

    if username != "admin":
        erros['username'] = 'Usuário sem permissão'
        erros['ok'] = False
        return JsonResponse(erros)

    if len(repr(pm25)) <= 0:
        erros['pm25'] = 'PM2.5 deve ser maior que 0'
        erros['ok'] = False
        return JsonResponse(erros)

    if len(repr(pm10)) <= 0:
        erros['pm10'] = 'PM10 deve ser maior que 0'
        erros['ok'] = False
        return JsonResponse(erros)
    
    if len(repr(co)) <= 0:
        erros['co'] = 'CO deve ser maior que 0'
        erros['ok'] = False
        return JsonResponse(erros)

    if len(co2) <= 0:
        erros['co2'] = 'CO2 deve ser maior que 0'
        erros['ok'] = False
        return JsonResponse(erros)

    if len(lpg) <= 0:
        erros['lpg'] = 'LPG deve ser maior que 0'
        erros['ok'] = False
        return JsonResponse(erros)

    if len(ch4) <= 0:
        erros['ch4'] = 'CH4 deve ser maior que 0'
        erros['ok'] = False
        return JsonResponse(erros)

    if len(humidity) <= 0:
        erros['umidade'] = 'Umidade deve ser maior que 0'
        erros['ok'] = False
        return JsonResponse(erros)
        
    if len(comment) > 300:
        erros['comentario'] = 'Máximo de 300 caractéres'
        erros['ok'] = False
        return JsonResponse(erros)

    if request.method == 'POST':
        user = username
        userid = list(Usuários.objects.filter(user=user).values('id'))[0]['id']
        empresa = Empresas.objects.get(id=empresa_id)
        Avaliações(comment=comment, grade=grade, pm25=pm25, pm10=pm10, co=co, co2=co2, lpg=lpg, ch4=ch4, humidity=humidity, temperature=temperature,
            empresa_id=empresa_id, user_id=userid, empresaname=empresa.name, username=user).save()
        media = Avaliações.objects.filter(empresa_id=empresa_id).aggregate(Avg('grade'))
        empresa.grade = round(media['grade__avg'])
        empresa.pm25 = pm25
        empresa.pm10 = pm10
        empresa.co = co
        empresa.co2 = co2
        empresa.lpg = lpg
        empresa.ch4 = ch4
        empresa.humidity = humidity
        empresa.temperature = temperature
        empresa.last_updated = datetime.now(timezone.utc)
        empresa.save()
        erros['ok'] = True
        return JsonResponse(erros)
        
    else:
        return JsonResponse({'ok':False})