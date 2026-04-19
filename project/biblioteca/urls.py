from django.urls import path
from . import views

urlpatterns = [
    path('', views.menu, name='menu'),
    path('login/', views.login_view, name='login'),
    path('catalogo/', views.catalogo, name='catalogo'),
    path('livro/<int:id>/', views.livro, name='livro'),
    path('livro/<int:id>/alerta/', views.criar_alerta, name='criar_alerta'),
    path('meus-livros/', views.meusLivros, name='meusLivros')
]
