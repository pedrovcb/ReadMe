from django.contrib import admin
from .models import Livro, Usuario, Emprestimo
from .models import AlertaLivroDisponivel

# Register your models here.

admin.site.register(Livro)
admin.site.register(Usuario)
admin.site.register(Emprestimo)
admin.site.register(AlertaLivroDisponivel)