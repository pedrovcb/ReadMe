from django.db import models
from datetime import date, timedelta
from django.contrib.auth.models import User

#Importando "Usuário" para emitir alerta sobre um livro disponível
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
    id_autenticado = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
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
    dataEmprestimo = models.DateField(default=date.today)
    dataDevolucao = models.DateField(default=devolucaoPadrao)
    renovacoes = models.IntegerField(default=0)
    maxRenovacoes = models.IntegerField(default=1)
    devolvido = models.BooleanField(default=False)

    @property
    def diasRestantes(self):
        return (self.dataDevolucao - date.today()).days

    @property
    def diasUsados(self):
        return (date.today() - self.dataEmprestimo).days

    @property
    def progresso(self):
        total = (self.dataDevolucao - self.dataEmprestimo).days
        if total == 0:
            return 0
        usados = self.diasUsados
        return min(int((usados / total) * 100), 100)

    def __str__(self):
        return f'{self.usuario.nome} - {self.livro.titulo}'
    
class AlertaLivroDisponivel(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    livro = models.ForeignKey('Livro', on_delete=models.CASCADE)
    ativo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.usuario} - {self.livro}"

