from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from .models import Livro, Usuario, Emprestimo

# Create your views here.

"""
def home(request):
    livros = Livro.objects.all()
    usuarios = Usuario.objects.all()
    emprestimos = Emprestimo.objects.filter(devolvido=False)
    return render(request, 'biblioteca/home.html', {
        'livros': livros,
        'usuarios': usuarios,
        'emprestimos': emprestimos
    })
"""

def cadastro(request):
    if request.method == 'POST':
        nome = request.POST.get('nome')
        email = request.POST.get('email')
        matricula = request.POST.get('matricula')
        usuario = request.POST.get('usuario')
        senha = request.POST.get('senha')
        confirmar_senha = request.POST.get('confirmar_senha')

        if senha != confirmar_senha:
            return render(request, 'cadastro.html', {'erro': 'As senhas não coincidem.'})

        if User.objects.filter(username=usuario).exists():
            return render(request, 'cadastro.html', {'erro': 'Esse nome de usuário já existe.'})

        if User.objects.filter(email=email).exists():
            return render(request, 'cadastro.html', {'erro': 'Esse email já está em uso.'})
        
        if Usuario.objects.filter(email=email).exists():
            return render(request, 'cadastro.html', {'erro': 'Esse email já está cadastrado na biblioteca.'})
        

        user = User.objects.create_user(
            username=usuario,
            email=email,
            password=senha
        )

        Usuario.objects.create(
            id_autenticado=user,
            nome=nome,
            email=email,
            matricula=matricula
        )

        login(request, user)
        return redirect('menu')

    return render(request, 'cadastro.html')

def login_view(request):
    if request.method == 'POST':
        usuario = request.POST.get('usuario')
        senha = request.POST.get('senha')

        user = authenticate(request, username=usuario, password=senha)

        if user is not None:
            login(request, user)
            return redirect('menu')
        else:
            return render(request, 'login.html', {'erro': 'Usuário ou senha inválidos.'})
    
    return render(request, 'login.html')


def menu(request):
    livro = None
    erro = None
    query = request.GET.get('q', '')
    if query:
        try:
            livro = Livro.objects.filter(titulo__icontains=query).first()
            if not livro:
                erro = 'Nenhum livro encontrado.'
        except:
            erro = 'Erro na pesquisa.'
    return render(request, 'biblioteca/menu.html', {'livro': livro, 'erro': erro, 'query': query})

def catalogo(request):
    livros = Livro.objects.all()
    return render(request, 'biblioteca/catalogo.html', {'livros': livros})

def livro(request, id):
    livro = Livro.objects.get(id=id)
    return render(request, 'biblioteca/livro.html', {'livro': livro})

def meusLivros(request):
    emprestimos = Emprestimo.objects.filter(devolvido=False)
    #usuario = Usuario.objects.get(id_autenticado=request.user) comentei aqui pq é uma função util no futuro
    return render(request, 'biblioteca/meusLivros.html', {'emprestimos': emprestimos})