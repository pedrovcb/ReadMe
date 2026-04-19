from django.shortcuts import render, redirect
from .models import Livro, Usuario, Emprestimo, AlertaLivroDisponivel
from django.contrib.auth.decorators import login_required
from django.contrib import messages

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

def login_view(request):
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