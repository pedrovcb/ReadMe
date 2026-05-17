from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings
from datetime import date, timedelta
from biblioteca.models import Emprestimo


class Command(BaseCommand):
    help = 'Envia e-mail de aviso de devolução para usuários com empréstimos próximos do vencimento'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dias',
            type=int,
            default=3,
            help='Avisar usuários com devolução em até X dias (padrão: 3)',
        )

    def handle(self, *args, **options):
        dias = options['dias']
        limite = date.today() + timedelta(days=dias)

        emprestimos = Emprestimo.objects.filter(
            devolvido=False,
            dataDevolucao__lte=limite,
            dataDevolucao__gte=date.today(),
            usuario__id_autenticado__isnull=False,
        ).select_related('usuario', 'livro', 'usuario__id_autenticado')

        if not emprestimos.exists():
            self.stdout.write(self.style.WARNING('Nenhum empréstimo próximo do vencimento encontrado.'))
            return

        enviados = 0
        erros = 0

        for emprestimo in emprestimos:
            usuario = emprestimo.usuario
            email = usuario.id_autenticado.email or usuario.email
            dias_restantes = emprestimo.diasRestantes

            if not email:
                self.stdout.write(self.style.WARNING(f'Usuário {usuario.nome} sem e-mail cadastrado. Pulando...'))
                continue

            assunto = f'[Biblioteca] Devolução do livro "{emprestimo.livro.titulo}" se aproxima!'

            if dias_restantes == 0:
                prazo_texto = 'hoje'
            elif dias_restantes == 1:
                prazo_texto = 'amanhã'
            else:
                prazo_texto = f'em {dias_restantes} dia(s)'

            mensagem = (
                f'Olá, {usuario.nome}!\n\n'
                f'Este é um lembrete automático da Biblioteca.\n\n'
                f'O livro "{emprestimo.livro.titulo}" deve ser devolvido {prazo_texto} '
                f'({emprestimo.dataDevolucao.strftime("%d/%m/%Y")}).\n\n'
                f'Caso precise, você ainda pode renovar o empréstimo pelo sistema.\n\n'
                f'Atenciosamente,\nBiblioteca ReadMe'
            )

            try:
                send_mail(
                    subject=assunto,
                    message=mensagem,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[email],
                    fail_silently=False,
                )
                self.stdout.write(self.style.SUCCESS(f'E-mail enviado para {usuario.nome} ({email})'))
                enviados += 1
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Erro ao enviar para {usuario.nome}: {e}'))
                erros += 1

        self.stdout.write(
            self.style.SUCCESS(f'\nConcluído: {enviados} e-mail(s) enviado(s), {erros} erro(s).')
        )
