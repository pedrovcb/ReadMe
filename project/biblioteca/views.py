import json
from django.shortcuts import render, redirect, get_object_or_404

from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from .models import Livro, Usuario, Emprestimo, AlertaLivroDisponivel
from django.http import JsonResponse
# Create your views here.

def home(request):
    livros = Livro.objects.all()[:20]

    context = {
        'livros': livros,
    }

    return render(request, 'biblioteca/home.html', context)

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

def alunos_com_livros(request):
    emprestimos_ativos = Emprestimo.objects.filter(devolvido=False).select_related("usuario", "livro")

    return render(request, "biblioteca/alunos_com_livros.html", {
        "emprestimos_ativos": emprestimos_ativos
    })

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

@login_required
def meusLivros(request):
    usuario = Usuario.objects.filter(id_autenticado=request.user).first()

    emprestimos = Emprestimo.objects.filter(
        usuario=usuario,
        devolvido=False
    )

    return render(request, 'biblioteca/meusLivros.html', {
        'emprestimos': emprestimos
    })

@login_required
def criar_alerta(request, id):
    livro = Livro.objects.get(id=id)

    alerta, criado = AlertaLivroDisponivel.objects.get_or_create(
        usuario=request.user,
        livro=livro,
        defaults={'ativo': True}
    )

    if not criado and not alerta.ativo:
        alerta.ativo = True
        alerta.save()

    messages.success(request, 'Alerta de disponibilidade ativado com sucesso.')
    return redirect('livro', id=livro.id)

def profDiciplinaCategoria(request):
    return render(request, 'profDiciplinaCategoria.html')

def salvar_livros(request):
    if request.method == 'POST':
        data = json.loads(request.body)

        for item in data:
            Livro.objects.create(
                titulo=item['titulo'],
                autor=item['autor'],
                quantidade=1
            )

        return JsonResponse({'status': 'ok'})
    
@login_required
def renovar_livro(request, id):
    if request.method == "POST":
        usuario = Usuario.objects.filter(id_autenticado=request.user).first()

        if not usuario:
            return redirect('cadastro')

        emprestimo = get_object_or_404(
            Emprestimo,
            id=id,
            usuario=usuario
        )

        emprestimo.renovar()

    return redirect('meusLivros')