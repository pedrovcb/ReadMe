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


# PÁGINA: cadastro.html


class PaginaCadastroTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse("cadastro")

    # --- Carregamento ---
    def test_pagina_carrega(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    # --- Conteúdo HTML ---
    def test_titulo_pagina(self):
        response = self.client.get(self.url)
        self.assertContains(response, "ReadMe - Cadastro")

    def test_heading_cadastro_visivel(self):
        response = self.client.get(self.url)
        self.assertContains(response, "Cadastro")

    # --- Links ---
    def test_link_para_login_presente(self):
        response = self.client.get(self.url)
        self.assertContains(response, reverse("login"))

    def test_link_para_menu_no_logo(self):
        response = self.client.get(self.url)
        self.assertContains(response, reverse("menu"))

    # --- Formulário ---
    def test_campo_nome_presente(self):
        response = self.client.get(self.url)
        self.assertContains(response, 'name="nome"')

    def test_campo_email_presente(self):
        response = self.client.get(self.url)
        self.assertContains(response, 'name="email"')

    def test_campo_matricula_presente(self):
        response = self.client.get(self.url)
        self.assertContains(response, 'name="matricula"')

    def test_campo_usuario_presente(self):
        response = self.client.get(self.url)
        self.assertContains(response, 'name="usuario"')

    def test_campos_senha_presentes(self):
        response = self.client.get(self.url)
        self.assertContains(response, 'name="senha"')
        self.assertContains(response, 'name="confirmar_senha"')

    def test_botao_criar_conta_presente(self):
        response = self.client.get(self.url)
        self.assertContains(response, "Criar conta")

    # --- Funcionamento do formulário ---
    def test_cadastro_valido_cria_usuario(self):
        self.client.post(self.url, {
            "nome": "Ana", "email": "ana@email.com", "matricula": "2024001",
            "usuario": "ana", "senha": "Senha@123", "confirmar_senha": "Senha@123",
        })
        self.assertTrue(User.objects.filter(username="ana").exists())

    def test_cadastro_valido_redireciona_para_menu(self):
        response = self.client.post(self.url, {
            "nome": "Ana", "email": "ana@email.com", "matricula": "2024001",
            "usuario": "ana", "senha": "Senha@123", "confirmar_senha": "Senha@123",
        })
        self.assertRedirects(response, reverse("menu"))

    def test_senhas_diferentes_exibe_erro(self):
        response = self.client.post(self.url, {
            "nome": "Ana", "email": "ana@email.com", "matricula": "2024001",
            "usuario": "ana", "senha": "Senha@123", "confirmar_senha": "Errada",
        })
        self.assertContains(response, "senhas não coincidem")

    def test_username_duplicado_exibe_erro(self):
        User.objects.create_user(username="ana", password="q")
        response = self.client.post(self.url, {
            "nome": "Ana", "email": "nova@email.com", "matricula": "2024002",
            "usuario": "ana", "senha": "Senha@123", "confirmar_senha": "Senha@123",
        })
        self.assertContains(response, "usuário já existe")

    def test_email_duplicado_exibe_erro(self):
        User.objects.create_user(username="outro", email="ana@email.com", password="q")
        response = self.client.post(self.url, {
            "nome": "Ana", "email": "ana@email.com", "matricula": "2024002",
            "usuario": "ana2", "senha": "Senha@123", "confirmar_senha": "Senha@123",
        })
        self.assertContains(response, "email já está em uso")



# PÁGINA: menu.html


class PaginaMenuTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse("menu")
        self.livro = Livro.objects.create(
            titulo="Dom Casmurro", autor="Machado de Assis", isbn="001"
        )

    # --- Carregamento ---
    def test_pagina_carrega(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    # --- Conteúdo HTML ---
    def test_texto_pesquise_um_livro_visivel(self):
        response = self.client.get(self.url)
        self.assertContains(response, "Pesquise um livro")

    # --- Formulário de busca ---
    def test_campo_busca_presente(self):
        response = self.client.get(self.url)
        self.assertContains(response, 'name="q"')

    def test_botao_pesquisar_presente(self):
        response = self.client.get(self.url)
        self.assertContains(response, "Pesquisar")

    # --- Funcionamento da busca ---
    def test_busca_livro_existente_exibe_titulo(self):
        response = self.client.get(self.url, {"q": "Dom Casmurro"})
        self.assertIsNotNone(response.context["livro"])
        self.assertContains(response, "Dom Casmurro")

    def test_busca_parcial_encontra_livro(self):
        response = self.client.get(self.url, {"q": "Dom"})
        self.assertIsNotNone(response.context["livro"])

    def test_busca_inexistente_exibe_erro(self):
        response = self.client.get(self.url, {"q": "Livro Fantasma"})
        self.assertContains(response, "Nenhum livro encontrado")

    def test_link_do_livro_encontrado_aponta_para_pagina_correta(self):
        response = self.client.get(self.url, {"q": "Dom Casmurro"})
        self.assertContains(response, reverse("livro", args=[self.livro.id]))



# PÁGINA: catalogo.html


class PaginaCatalogoTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse("catalogo")
        self.livro1 = Livro.objects.create(
            titulo="O Cortico", autor="Aluisio Azevedo", isbn="002", disponivel=True
        )
        self.livro2 = Livro.objects.create(
            titulo="Iracema", autor="Jose de Alencar", isbn="003", disponivel=False
        )

    # --- Carregamento ---
    def test_pagina_carrega(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    # --- Conteúdo HTML ---
    def test_heading_livros_disponiveis(self):
        response = self.client.get(self.url)
        self.assertContains(response, "Livros")

    def test_todos_os_livros_aparecem(self):
        response = self.client.get(self.url)
        self.assertContains(response, "O Cortico")
        self.assertContains(response, "Iracema")

    def test_badge_disponivel_aparece(self):
        response = self.client.get(self.url)
        self.assertContains(response, "Disponível")

    def test_badge_reservado_aparece(self):
        response = self.client.get(self.url)
        self.assertContains(response, "Reservado")

    def test_catalogo_vazio_exibe_mensagem(self):
        Livro.objects.all().delete()
        response = self.client.get(self.url)
        self.assertContains(response, "Nenhum livro cadastrado")

    # --- Links ---
    def test_cada_livro_tem_link_para_sua_pagina(self):
        response = self.client.get(self.url)
        self.assertContains(response, reverse("livro", args=[self.livro1.id]))
        self.assertContains(response, reverse("livro", args=[self.livro2.id]))



