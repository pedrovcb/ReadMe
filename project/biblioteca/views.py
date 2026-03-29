from django.shortcuts import render
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
    return render(request, 'login.html')

def menu(request):
    return render(request, 'biblioteca/menu.html')

def catalogo(request):
    livros = Livro.objects.all()
    return render(request, 'biblioteca/catalogo.html', {'livros': livros})

def livro(request, id):
    livro = Livro.objects.get(id=id)
    return render(request, 'biblioteca/livro.html', {'livro': livro})

def meusLivros(request):
    emprestimos = Emprestimo.objects.filter(devolvido=False)
    return render(request, 'biblioteca/meusLivros.html', {'emprestimos': emprestimos})