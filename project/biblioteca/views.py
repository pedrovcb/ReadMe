from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from .models import Livro, Usuario, Emprestimo

# Create your views here.

""""
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


def loginView(request):
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
    return render(request, 'biblioteca/meusLivros.html', {'emprestimos': emprestimos})