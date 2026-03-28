from django.shortcuts import render
from .models import Livro, Usuario, Emprestimo

# Create your views here.

def home(request):
    livros = Livro.objects.all()
    usuarios = Usuario.objects.all()
    emprestimos = Emprestimo.objects.filter(devolvido=False)
    return render(request, 'biblioteca/home.html', {
        'livros': livros,
        'usuarios': usuarios,
        'emprestimos': emprestimos
    })