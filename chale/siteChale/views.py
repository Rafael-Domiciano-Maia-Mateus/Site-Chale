from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login 
from django.contrib import messages
from django.contrib.auth.models import User
from .forms import FotoForm  
from .models import Foto
from django.contrib.auth.decorators import login_required, user_passes_test


# Create your views here.
def eh_admin(user):
  '''
  Verifica se o usuário tem permissões de administrador.

  Esta função verifica se o usuário é um administrador no sistema, baseado em duas propriedades do objeto `user`:
  - Se o usuário é um "staff" (funcionário), o que significa que ele tem permissões administrativas no Django.
  - Se o usuário é um "superusuário", o que significa que ele tem todas as permissões no sistema.

  Parâmetros:
  - user (User): O objeto `User` do Django que representa o usuário a ser verificado.

  Fluxo:
  1. A função verifica se o usuário tem a propriedade `is_staff` ou `is_superuser` como `True`.
  2. Se qualquer uma dessas propriedades for `True`, o usuário é considerado um administrador.
  3. Caso contrário, o usuário não é considerado um administrador.

  Retorna:
  bool: Retorna `True` se o usuário for um administrador, ou `False` caso contrário.
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


def minha_conta(request): 
  return render(request, 'minha_conta.html')


def ajuda(request):
  return render(request, 'ajuda.html')


def reservas(request):
  return render(request, 'reservas.html')


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


def login_view(request):
  '''
  Exibe a página de login e processa as tentativas de autenticação de usuários.

  Este view trata tanto requisições GET quanto POST:
  - Em requisições GET, apenas renderiza a página de login.
  - Em requisições POST, tenta autenticar o usuário com os dados fornecidos.

  Parâmetros:
  request (HttpRequest): O objeto da requisição HTTP, que pode conter dados de login enviados via POST.

  Fluxo:
  1. Verifica se o método da requisição é POST.
  2. Obtém os campos 'username' e 'password' do corpo da requisição.
  3. Se algum dos campos estiver vazio, retorna um erro e renderiza novamente a página de login.
  4. Caso contrário, tenta autenticar o usuário com as credenciais fornecidas.
    - Se a autenticação for bem-sucedida e o usuário estiver ativo, realiza o login, exibe uma mensagem de boas-vindas e redireciona para a homepage.
    - Se o usuário estiver inativo, exibe uma mensagem de erro.
    - Se a autenticação falhar, exibe uma mensagem de erro de credenciais inválidas.
  5. Em qualquer caso de falha, a página de login é renderizada novamente com as mensagens apropriadas.

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
  Exibe a página de registro e processa a criação de novos usuários.

  Este view trata requisições GET e POST:
  - Em requisições GET, renderiza o formulário de registro.
  - Em requisições POST, valida os dados recebidos e cria uma nova conta de usuário, se estiverem corretos.

  Parâmetros:
  request (HttpRequest): O objeto da requisição HTTP contendo, possivelmente, os dados do formulário de cadastro.

  Fluxo:
  1. Verifica se o método da requisição é POST.
  2. Coleta os campos 'username', 'email', 'password' e 'confirm_password' do formulário.
  3. Valida os dados:
     - Verifica se as senhas coincidem.
     - Verifica se o nome de usuário já está em uso.
     - Verifica se o e-mail já está cadastrado.
  4. Caso alguma validação falhe, exibe a mensagem de erro correspondente e renderiza novamente a página de registro.
  5. Se todas as validações forem aprovadas, cria um novo usuário com os dados fornecidos e salva no banco de dados.
  6. Exibe uma mensagem de sucesso e redireciona o usuário para a página de login.

  Retorna:
  HttpResponse: A página de registro renderizada com mensagens, ou um redirecionamento para a página de login após o cadastro bem-sucedido.
  '''

  if request.method == 'POST':
    username = request.POST.get('username')
    email = request.POST.get('email')
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
    messages.success(request, 'Cadastro realizado com sucesso! Faça login.')
    return redirect('login')
  return render(request, 'register.html')
