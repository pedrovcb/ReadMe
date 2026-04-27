from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from datetime import date, timedelta
from biblioteca.models import Livro, Usuario, Emprestimo, AlertaLivroDisponivel


# PÁGINA: login.html

class PaginaLoginTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse("login")
        User.objects.create_user(username="joao", password="senha123")

    # --- Carregamento ---
    def test_pagina_carrega(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    # --- Conteúdo HTML ---
    def test_titulo_pagina(self):
        response = self.client.get(self.url)
        self.assertContains(response, "ReadMe - Login")

    def test_texto_log_in_visivel(self):
        response = self.client.get(self.url)
        self.assertContains(response, "Log In")

    # --- Formulário ---
    def test_campo_usuario_presente(self):
        response = self.client.get(self.url)
        self.assertContains(response, 'name="usuario"')

    def test_campo_senha_presente(self):
        response = self.client.get(self.url)
        self.assertContains(response, 'name="senha"')

    def test_botao_submit_presente(self):
        response = self.client.get(self.url)
        self.assertContains(response, 'type="submit"')

    # --- Funcionamento do formulário ---
    def test_login_valido_redireciona_para_menu(self):
        response = self.client.post(self.url, {"usuario": "joao", "senha": "senha123"})
        self.assertRedirects(response, reverse("menu"))

    def test_login_senha_errada_exibe_erro(self):
        response = self.client.post(self.url, {"usuario": "joao", "senha": "errada"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "inválidos")

    def test_login_usuario_inexistente_exibe_erro(self):
        response = self.client.post(self.url, {"usuario": "ninguem", "senha": "123"})
        self.assertContains(response, "inválidos")

