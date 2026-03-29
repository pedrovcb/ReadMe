from django.urls import path
from . import views

urlpatterns = [
    path('', views.menu, name='menu'),
    path('login/', views.loginView, name='login'),
    path('catalogo/', views.catalogo, name='catalogo'),
    path('livro/<int:id>/', views.livro, name='livro'),
    path('meus-livros/', views.meusLivros, name='meusLivros'),
]
