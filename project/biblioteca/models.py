from django.db import models
from datetime import date, timedelta

# Create your models here.

class Livro(models.Model):
    titulo = models.CharField(max_length=500)
    autor = models.CharField(max_length=200)
    isbn = models.CharField(max_length=13)
    quantidade = models.IntegerField(default=1)
    capa = models.ImageField(upload_to='capas/', blank=True, null=True)
    disponivel = models.BooleanField(default=True)

    def __str__(self):
        return self.titulo
    

class Usuario(models.Model):
    nome = models.CharField(max_length=200)
    email = models.EmailField(unique=True)
    matricula = models.CharField(max_length=10)

    def __str__(self):
        return self.nome
    

def devolucaoPadrao():
    return date.today() + timedelta(days=10)
    
class Emprestimo(models.Model):
    livro = models.ForeignKey(Livro, on_delete=models.CASCADE)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    dataEmprestimo = models.DateField(auto_now_add=True)
    dataDevolucao = models.DateField(default = devolucaoPadrao)
    renovacoes = models.IntegerField(default=0)
    maxRenovacoes = models.IntegerField(default=1)
    devolvido = models.BooleanField(default=False)

    def diasRestantes(self):
        return(self.dataDevolucao - date.today()).days

    def __str__(self):
        return f'{self.membro.nome} - {self.livro.titulo}'
