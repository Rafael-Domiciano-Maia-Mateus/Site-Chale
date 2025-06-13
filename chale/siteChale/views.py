from datetime import datetime, date, timedelta
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
import matplotlib.pyplot as plt
import io
from .forms import *
from .models import *


# Create your views here.
def eh_admin(user):
    '''
    Verifica se o usuário tem permissões de administrador.

    Esta função verifica se o usuário é um administrador no sistema, baseado em duas propriedades do objeto user:
    - Se o usuário é um "staff" (funcionário), o que significa que ele tem permissões administrativas no Django.
    - Se o usuário é um "superusuário", o que significa que ele tem todas as permissões no sistema.

    Parâmetros:
    - user (User): O objeto User do Django que representa o usuário a ser verificado.

    Retorna:
    bool: Retorna True se o usuário for um administrador, ou False caso contrário.
    '''
    return user.is_staff or user.is_superuser


def homepage(request):
    '''
    Função que processa a requisição para a página inicial.

    Essa função recupera todas as fotos do banco de dados e as envia
    para a template 'homepage.html' para exibição.

    Parâmetros:
    request (HttpRequest): Objeto que contém os dados da requisição HTTP.

    Retorna:
    HttpResponse: A resposta renderizada com as fotos para exibição na página inicial.
    '''
    fotos = Foto.objects.all()
    return render(request, 'homepage.html', {'fotos': fotos})


def administracao(request):
    return render(request, 'administracao.html')


def minha_conta(request):
    cliente = Cliente.objects.get(usuario=request.user)
    nome = cliente.nome
    email = cliente.email
    telefone = cliente.telefone
    return render(request, 'minha_conta.html', {
        'nome': nome,
        'email': email,
        'telefone': telefone,
    })


def ajuda(request):
    return render(request, 'ajuda.html')


def obter_max_pessoas(request):
    '''
    Função que processa a requisição para obter o número máximo de pessoas de um chalé.

    Essa função recupera o ID do chalé a partir dos parâmetros da requisição GET,
    busca o chalé correspondente no banco de dados e retorna a quantidade máxima
    de pessoas permitidas em formato JSON. Caso o chalé não seja encontrado, retorna 0.

    Parâmetros:
    request (HttpRequest): Objeto que contém os dados da requisição HTTP.

    Retorna:
    JsonResponse: Um objeto JSON contendo a chave 'max_pessoas' com o valor da capacidade
    máxima do chalé ou 0 se o chalé não existir.
    '''
    chale_id = request.GET.get('chale_id')
    try:
        chale = Chale.objects.get(id=chale_id)
        return JsonResponse({'max_pessoas': chale.max_pessoas})  
    except Chale.DoesNotExist:
        return JsonResponse({'max_pessoas': 0})


def home_reservas(request):
    return render(request, 'home_reservas.html')


@login_required
def reservas(request):
    '''
    Função que processa a requisição para a página de reservas.

    Essa função lida com a criação de uma nova reserva. Se a requisição for POST,
    ela valida os dados do formulário, verifica se a quantidade de pessoas não excede
    a capacidade máxima do chalé e, se tudo estiver correto, salva a reserva no banco
    de dados. Em caso de erro na validação ou no número de pessoas, exibe mensagens de erro.
    Se a requisição for GET, exibe o formulário vazio para preenchimento.

    Parâmetros:
    request (HttpRequest): Objeto que contém os dados da requisição HTTP.

    Retorna:
    HttpResponse: A resposta renderizada com o formulário de reserva ou um redirecionamento
    para a página de finalização da reserva em caso de sucesso.
    '''
    if request.method == 'POST':
        form = ReservaForm(request.POST)
        if form.is_valid():
            chale = form.cleaned_data['chale']
            checkin = form.cleaned_data['checkin']
            checkout = form.cleaned_data['checkout']
            qtd_pessoas = form.cleaned_data['qtd_pessoas']
            telefone = form.cleaned_data['telefone']

            try:
                qtd_pessoas = int(qtd_pessoas)
            except ValueError:
                messages.error(request, 'Quantidade de pessoas inválida.')
                return redirect('reservas')

            if qtd_pessoas > chale.max_pessoas:
                messages.error(request, f'O número de pessoas excede a capacidade máxima do chalé {chale.nomeChale}.')
                return redirect('reservas')

            reserva = Reserva(
                chale=chale,  
                checkin=checkin,
                checkout=checkout,
                quantidadePessoas=qtd_pessoas,
                telefone=telefone
            )

            reserva.save()

            return redirect('finalizar', reserva_id=reserva.id) 
    else:
        form = ReservaForm()

    return render(request, 'reservas.html', {'form': form})


def verificar_disponibilidade(request):
    '''
    Função que verifica a disponibilidade de um chalé para reserva.

    Essa função recebe o ID do chalé, a data de check-in e a data de check-out
    a partir dos parâmetros da requisição GET. Em seguida, verifica se existem
    reservas que conflitam com o período informado. Retorna um JSON indicando
    se o chalé está disponível ou não.

    Parâmetros:
    request (HttpRequest): Objeto que contém os dados da requisição HTTP.

    Retorna:
    JsonResponse: Um objeto JSON contendo a chave 'disponivel' com valor True
    se o chalé estiver disponível, ou False se já houver conflito de reserva.
    '''
    chale_id = request.GET.get('chale')
    checkin = request.GET.get('checkin')
    checkout = request.GET.get('checkout')

    reservas = Reserva.objects.filter(
        chale_id=chale_id,
        checkin__lt=checkout,
        checkout__gt=checkin
    )

    return JsonResponse({'disponivel': not reservas.exists()})


def datas_indisponiveis(request):
    '''
    Função que retorna todas as datas indisponíveis para reserva.

    Essa função percorre todas as reservas cadastradas no banco de dados,
    gera a lista de todas as datas entre o check-in e o check-out (inclusive),
    e retorna essas datas no formato 'YYYY-MM-DD' em um objeto JSON.

    Parâmetros:
    request (HttpRequest): Objeto que contém os dados da requisição HTTP.

    Retorna:
    JsonResponse: Um objeto JSON contendo a chave 'datas_indisponiveis' com
    uma lista de todas as datas já reservadas.
    '''
    datas_indisponiveis = []

    reservas = Reserva.objects.all()

    for reserva in reservas:
        checkin = reserva.checkin
        checkout = reserva.checkout

        while checkin <= checkout:
            datas_indisponiveis.append(checkin.strftime('%Y-%m-%d'))
            checkin += timedelta(days=1)
    return JsonResponse({'datas_indisponiveis': datas_indisponiveis}, safe=False)


def finalizar(request, reserva_id):
    '''
    Função que processa a página de finalização da reserva.

    Essa função recupera a reserva com base no ID fornecido, calcula o valor total
    da hospedagem (considerando o preço do chalé por dia mais a taxa cadastrada para o chalé),
    formata o valor total para o padrão brasileiro e envia essas informações
    para a template 'finalizar.html' para exibição.

    Parâmetros:
    request (HttpRequest): Objeto que contém os dados da requisição HTTP.
    reserva_id (int): ID da reserva a ser finalizada.

    Retorna:
    HttpResponse: A resposta renderizada com os detalhes da reserva para finalização.
    '''
    reserva = get_object_or_404(Reserva, id=reserva_id)
    chale = reserva.chale
    checkin = reserva.checkin
    checkout = reserva.checkout
    qtd = reserva.quantidadePessoas
    dias = (checkout - checkin).days
    preco_chale = chale.preco
    taxa = chale.taxa

    valor_total = reserva.precoTotal()  

    valor_formatado = f"R$ {valor_total:.2f}".replace('.', ',')

    return render(request, 'finalizar.html', {
        'chale': chale.nomeChale,
        'checkin': checkin,
        'checkout': checkout,
        'qtd': qtd,
        'dias': dias,
        'valor_total': valor_formatado,
        'taxa': taxa,
    })


def galeria(request):
    '''
    Função que processa a requisição para a página da galeria.

    Essa função recupera todas as fotos do banco de dados e as envia
    para a template 'galeria.html' para exibição na página de galeria.

    Parâmetros:
    request (HttpRequest): Objeto que contém os dados da requisição HTTP.

    Retorna:
    HttpResponse: A resposta renderizada com as fotos para exibição na galeria.
    '''
    fotos = Foto.objects.all()
    return render(request, 'galeria.html', {'fotos': fotos})


@login_required
@user_passes_test(eh_admin)
def upload_foto(request):
    '''
    Função que processa a requisição para o upload de fotos.

    Essa função permite que apenas usuários autenticados e com permissão de administrador
    possam fazer o upload de fotos. Ela valida o formulário e, se válido, salva a foto no banco
    de dados e redireciona o usuário para a página inicial.

    Parâmetros:
    request (HttpRequest): Objeto que contém os dados da requisição HTTP.

    Retorna:
    HttpResponse: A resposta renderizada com o formulário para upload de foto, ou redireciona para 
    a homepage após o upload bem-sucedido.
    '''
    if request.method == 'POST':
        form = FotoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('homepage')  
    else:
        form = FotoForm()
    return render(request, 'upload_foto.html', {'form': form})


def home_reservas(request):
    cliente = Cliente.objects.get(usuario=request.user)
    reserva = Reserva.objects.filter(cliente=cliente).last()
    return render(request, 'home_reservas.html', {
        'nome': cliente.nome if reserva else '',
        'email': cliente.email if reserva else '',
        'telefone': cliente.telefone if reserva else '',
        'chale': reserva.chale.nomeChale if reserva else '',
        'checkin': reserva.checkin if reserva else '',
        'checkout': reserva.checkout if reserva else '',
        'numero_pessoas': reserva.quantidadePessoas if reserva else '',
    })


def chat(request):
    return render(request, 'chat.html')


def NovoLogin(request):
    return render(request, 'NovoLogin.html')
    

def login_view(request):
    '''
    Exibe a página de login e processa as tentativas de autenticação de usuários.

    Este view trata tanto requisições GET quanto POST:
    - Em requisições GET, apenas renderiza a página de login.
    - Em requisições POST, tenta autenticar o usuário com os dados fornecidos.

    Parâmetros:
    request (HttpRequest): O objeto da requisição HTTP, que pode conter dados de login enviados via POST.

    Retorna:
    HttpResponse: A página de login renderizada, ou um redirecionamento para a homepage em caso de sucesso.
    '''

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        if not username or not password:
            messages.error(request, 'Todos os campos são obrigatórios.')
            return render(request, 'login.html')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            if user.is_active:
                login(request, user)
                messages.success(request, f'Bem-vindo, {user.username}!')
                return redirect('homepage')  
            else:
                messages.error(request, 'Esta conta está desativada.')
        else:
            messages.error(request, 'Nome de usuário ou senha inválidos.')
            
        return render(request, 'login.html')
    return render(request, 'login.html')


def register(request):
    '''
    View para cadastro de novos usuários.

    Esta view gerencia o processo de registro de usuários no sistema. Ela trata a submissão
    do formulário de cadastro, realiza validações básicas (como senha confirmada, unicidade de 
    nome de usuário e e-mail) e cria as instâncias correspondentes de `User` e `Cliente`.

    Parâmetros:
    - request (HttpRequest): Objeto de requisição contendo dados do formulário.

    Retorna:
    - HttpResponse: Renderiza a página de registro (`register.html`) ou redireciona para o login em caso de sucesso.
    '''
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        telefone = request.POST.get('telefone')  
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password != confirm_password:
            messages.error(request, 'As senhas não coincidem.')
            return render(request, 'register.html')
            
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Nome de usuário já está em uso.')
            return render(request, 'register.html')
            
        if User.objects.filter(email=email).exists():
            messages.error(request, 'E-mail já está em uso.')
            return render(request, 'register.html')
            
        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()

        Cliente.objects.create(usuario=user, nome=username, email=email, telefone=telefone)

        messages.success(request, 'Cadastro realizado com sucesso! Faça login.')
        return redirect('login')

    return render(request, 'register.html')


def recuperarSenha(request):
    return render(request, 'recuperarSenha.html')
