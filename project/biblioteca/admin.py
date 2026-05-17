from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.utils import timezone
from django.db.models import Count, Q
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.contrib import messages
from datetime import date
from .models import Livro, Usuario, Emprestimo, AlertaLivroDisponivel


@admin.register(Livro)
class LivroAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'autor', 'isbn', 'quantidade', 'disponivel', 'total_emprestimos_ativos')
    list_filter = ('disponivel', 'autor')
    search_fields = ('titulo', 'autor', 'isbn')
    list_editable = ('quantidade', 'disponivel')
    readonly_fields = ('total_emprestimos_ativos',)
    ordering = ('titulo',)
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('titulo', 'autor', 'isbn', 'capa')
        }),
        ('Controle de Estoque', {
            'fields': ('quantidade', 'disponivel', 'total_emprestimos_ativos'),
            'classes': ('collapse',)
        }),
    )
    
    @admin.display(description='Quantidade')
    def quantidade_display(self, obj):
        if obj.quantidade <= 0:
            return format_html('<span style="color: red; font-weight: bold;">{}</span>', obj.quantidade)
        elif obj.quantidade <= 2:
            return format_html('<span style="color: orange; font-weight: bold;">{}</span>', obj.quantidade)
        return obj.quantidade
    
    @admin.display(description='Disponível')
    def disponivel_status(self, obj):
        if obj.disponivel:
            return mark_safe('<img src="/static/admin/img/icon-yes.svg" alt="Sim">')
        return mark_safe('<img src="/static/admin/img/icon-no.svg" alt="Não">')
    
    @admin.display(description='Empréstimos Ativos')
    def total_emprestimos_ativos(self, obj):
        return obj.emprestimo_set.filter(devolvido=False).count()
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.annotate(
            emprestimos_ativos=Count('emprestimo', filter=Q(emprestimo__devolvido=False))
        )


@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ('nome', 'email', 'matricula', 'is_professor_status', 'total_emprestimos_ativos', 'total_emprestimos_historico')
    list_filter = ('is_professor',)
    search_fields = ('nome', 'email', 'matricula')
    readonly_fields = ('total_emprestimos_ativos', 'total_emprestimos_historico', 'historico_emprestimos')
    ordering = ('nome',)
    
    fieldsets = (
        ('Informações Pessoais', {
            'fields': ('nome', 'email', 'matricula', 'id_autenticado')
        }),
        ('Tipo de Usuário', {
            'fields': ('is_professor',)
        }),
        ('Estatísticas de Empréstimos', {
            'fields': ('total_emprestimos_ativos', 'total_emprestimos_historico', 'historico_emprestimos'),
            'classes': ('collapse',)
        }),
    )
    
    @admin.display(description='Professor')
    def is_professor_status(self, obj):
        if obj.is_professor:
            return mark_safe('<span style="color: green; font-weight: bold;">Sim</span>')
        return mark_safe('<span style="color: gray;">Não</span>')
    
    @admin.display(description='Empréstimos Ativos')
    def total_emprestimos_ativos(self, obj):
        return obj.emprestimo_set.filter(devolvido=False).count()
    
    @admin.display(description='Total Histórico')
    def total_emprestimos_historico(self, obj):
        return obj.emprestimo_set.count()
    
    @admin.display(description='Histórico de Empréstimos')
    def historico_emprestimos(self, obj):
        emprestimos = obj.emprestimo_set.all().order_by('-dataEmprestimo')[:10]

        if not emprestimos:
            return "Nenhum empréstimo registrado"
        
        html = '<ul style="margin: 0; padding-left: 20px;">'

        for emp in emprestimos:
            status = '<span style="color: green;">Devolvido</span>' if emp.devolvido else '<span style="color: red;">Ativo</span>'
            html += f'<li>{emp.livro.titulo} - {emp.dataEmprestimo} ({status})</li>'

        html += '</ul>'

        return mark_safe(html)


class EmprestimoActionsMixin:
    actions = ['marcar_como_devolvido', 'renovar_emprestimo', 'enviar_lembrete_devolucao']
    
    @admin.action(description='Marcar como devolvido')
    def marcar_como_devolvido(self, request, queryset):
        atualizados = 0

        for emprestimo in queryset.filter(devolvido=False):
            emprestimo.devolvido = True
            emprestimo.save()

            livro = emprestimo.livro
            livro.quantidade += 1

            if livro.quantidade > 0:
                livro.disponivel = True

            livro.save()
            atualizados += 1
        
        self.message_user(request, f'{atualizados} empréstimo(s) marcado(s) como devolvido(s).')
    
    @admin.action(description='Renovar empréstimo')
    def renovar_emprestimo(self, request, queryset):
        renovados = 0

        for emprestimo in queryset.filter(devolvido=False):
            if emprestimo.renovar():
                renovados += 1
        
        self.message_user(request, f'{renovados} empréstimo(s) renovado(s) com sucesso.')
    
    @admin.action(description='Enviar lembrete de devolução')
    def enviar_lembrete_devolucao(self, request, queryset):
        self.message_user(request, f'Lembretes de devolução enviados para {queryset.count()} usuário(s).')


@admin.register(Emprestimo)
class EmprestimoAdmin(EmprestimoActionsMixin, admin.ModelAdmin):
    list_display = (
        'usuario', 
        'livro', 
        'data_emprestimo_formatada', 
        'data_devolucao_formatada', 
        'dias_restantes_display', 
        'progresso_bar', 
        'devolvido_status',
        'renovacoes_display'
    )

    list_filter = ('devolvido', 'dataEmprestimo', 'dataDevolucao')
    search_fields = ('usuario__nome', 'livro__titulo', 'livro__autor')
    readonly_fields = ('diasRestantes', 'progresso', 'progresso_bar_visual', 'dias_usados', 'renovacoes_restantes')
    ordering = ('-dataEmprestimo',)
    date_hierarchy = 'dataEmprestimo'
    
    fieldsets = (
        ('Informações do Empréstimo', {
            'fields': ('livro', 'usuario', 'dataEmprestimo', 'dataDevolucao')
        }),
        ('Status e Controle', {
            'fields': ('devolvido', 'renovacoes', 'maxRenovacoes')
        }),
        ('Métricas', {
            'fields': ('diasRestantes', 'dias_usados', 'progresso', 'progresso_bar_visual', 'renovacoes_restantes'),
            'classes': ('collapse',)
        }),
    )
    
    @admin.display(description='Data Empréstimo')
    def data_emprestimo_formatada(self, obj):
        return obj.dataEmprestimo.strftime('%d/%m/%Y')
    
    @admin.display(description='Data Devolução')
    def data_devolucao_formatada(self, obj):
        return obj.dataDevolucao.strftime('%d/%m/%Y')
    
    @admin.display(description='Dias Restantes')
    def dias_restantes_display(self, obj):
        dias = obj.diasRestantes

        if obj.devolvido:
            return mark_safe('<span style="color: gray;">Devolvido</span>')
        elif dias < 0:
            return format_html(
                '<span style="color: red; font-weight: bold;">{}</span>',
                f'Atrasado {-dias} dias'
            )
        elif dias <= 3:
            return format_html(
                '<span style="color: orange; font-weight: bold;">{} dias</span>',
                dias
            )

        return format_html(
            '<span style="color: green;">{} dias</span>',
            dias
        )
    
    @admin.display(description='Progresso')
    def progresso_bar(self, obj):
        progresso = obj.progresso

        if progresso >= 90:
            color = 'red'
        elif progresso >= 70:
            color = 'orange'
        else:
            color = 'green'
        
        return format_html(
            '<div style="width: 100px; background: #e0e0e0; border-radius: 5px;">'
            '<div style="width: {}%; background: {}; height: 15px; border-radius: 5px;"></div>'
            '</div>',
            progresso,
            color
        )
    
    @admin.display(description='Devolvido')
    def devolvido_status(self, obj):
        if obj.devolvido:
            return mark_safe('<img src="/static/admin/img/icon-yes.svg" alt="Sim">')
        return mark_safe('<img src="/static/admin/img/icon-no.svg" alt="Não">')
    
    @admin.display(description='Renovações')
    def renovacoes_display(self, obj):
        return f'{obj.renovacoes}/{obj.maxRenovacoes}'
    
    @admin.display(description='Dias Usados')
    def dias_usados(self, obj):
        return obj.diasUsados
    
    @admin.display(description='Progresso Visual')
    def progresso_bar_visual(self, obj):
        progresso = obj.progresso

        if progresso >= 90:
            color = 'red'
        elif progresso >= 70:
            color = 'orange'
        else:
            color = 'green'
        
        return format_html(
            '<div style="width: 200px; background: #e0e0e0; border-radius: 5px;">'
            '<div style="width: {}%; background: {}; height: 20px; border-radius: 5px;"></div>'
            '</div><span>{}%</span>',
            progresso,
            color,
            progresso
        )
    
    @admin.display(description='Renovações Restantes')
    def renovacoes_restantes(self, obj):
        return obj.renovacoes_restantes
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('usuario', 'livro')
    
    def has_add_permission(self, request):
        return False


@admin.register(AlertaLivroDisponivel)
class AlertaLivroDisponivelAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'livro', 'ativo_status', 'data_criacao')
    list_filter = ('ativo',)
    search_fields = ('usuario__username', 'livro__titulo')
    readonly_fields = ('data_criacao',)
    ordering = ('-id',)
    
    @admin.display(description='Ativo')
    def ativo_status(self, obj):
        if obj.ativo:
            return mark_safe('<img src="/static/admin/img/icon-yes.svg" alt="Sim">')
        return mark_safe('<img src="/static/admin/img/icon-no.svg" alt="Não">')
    
    @admin.display(description='Data Criação')
    def data_criacao(self, obj):
        return getattr(obj, 'created_at', 'N/A')


admin.site.site_header = "ReadMe - Painel Administrativo"
admin.site.site_title = "ReadMe Admin"
admin.site.index_title = "Gerenciamento do Acervo"