from django.db.models import Count
from datetime import date
from biblioteca.models import Livro, Emprestimo


def admin_dashboard_data(request):
    if request.path.startswith('/admin/'):
        return {
            'total_livros': Livro.objects.count(),
            'livros_disponiveis': Livro.objects.filter(disponivel=True).count(),
            'emprestimos_ativos': Emprestimo.objects.filter(devolvido=False).count(),
            'emprestimos_atrasados': Emprestimo.objects.filter(
                devolvido=False,
                dataDevolucao__lt=date.today()
            ).count(),
            'emprestimos_recentes': Emprestimo.objects.select_related(
                'usuario', 'livro'
            ).order_by('-dataEmprestimo')[:5],
            'livros_populares': Livro.objects.annotate(
                total_emprestimos=Count('emprestimo')
            ).order_by('-total_emprestimos')[:5],
        }
    return {}
