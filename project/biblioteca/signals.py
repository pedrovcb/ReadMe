from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from .models import Livro, AlertaLivroDisponivel

@receiver(post_save, sender=Livro)
def avisar_disponibilidade(sender, instance, created, **kwargs):
    if instance.disponivel:
        alertas = AlertaLivroDisponivel.objects.filter(
            livro=instance,
            ativo=True
        ).select_related('usuario')

        for alerta in alertas:
            if alerta.usuario.email:
                send_mail(
                    subject='Livro disponível novamente',
                    message=f'O livro "{instance.titulo}" está disponível novamente.',
                    from_email=None,
                    recipient_list=[alerta.usuario.email],
                    fail_silently=True
                )

            alerta.ativo = False
            alerta.save()