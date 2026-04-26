let livros = JSON.parse(localStorage.getItem('livros')) || [];
let editandoIndex = null;

function salvarNoStorage() {
    localStorage.setItem('livros', JSON.stringify(livros));
}


function adicionarCategoria() {
    const input = document.getElementById('input-categoria');
    const nome = input.value.trim();

    if (!nome) return alert('Digite o nome da categoria!');

    // Adiciona na lista visual
    const ul = document.querySelector('#categorias ul');
    const li = document.createElement('li');
    li.textContent = nome;

    const btnRemover = document.createElement('button');
    btnRemover.textContent = 'Remover';
    btnRemover.onclick = () => {
        ul.removeChild(li);
        removerOptionDoSelect(nome);
    };

    li.appendChild(btnRemover);
    ul.appendChild(li);

    // Adiciona no select de livros
    const select = document.getElementById('select-categoria');
    const option = document.createElement('option');
    option.value = nome;
    option.textContent = nome;
    select.appendChild(option);

    input.value = '';
}

function removerOptionDoSelect(nome) {
    const select = document.getElementById('select-categoria');
    for (let option of select.options) {
        if (option.value === nome) {
            select.removeChild(option);
            break;
        }
    }
}

function adicionarLivro() {
    const titulo = document.getElementById('input-titulo').value.trim();
    const autor = document.getElementById('input-autor').value.trim();
    const categoria = document.getElementById('select-categoria').value;

    if (!titulo || !autor || !categoria) {
        return alert('Preencha todos os campos!');
    }

    if (editandoIndex !== null) {
        // Modo edição: atualiza o livro existente
        livros[editandoIndex] = { titulo, autor, categoria };
        editandoIndex = null;
        document.getElementById('btn-livro').textContent = 'Adicionar livro';
    } else {
        // Modo adição: cria novo livro
        livros.push({ titulo, autor, categoria });
    }

    salvarNoStorage();
    renderizarLivros();
    limparFormularioLivro();
}

function removerLivro(index) {
    livros.splice(index, 1);
    salvarNoStorage();
    renderizarLivros();
}

function editarLivro(index) {
    const livro = livros[index];

    document.getElementById('input-titulo').value = livro.titulo;
    document.getElementById('input-autor').value = livro.autor;
    document.getElementById('select-categoria').value = livro.categoria;
    document.getElementById('btn-livro').textContent = 'Salvar edição';

    editandoIndex = index;
}

function renderizarLivros() {
    const ul = document.getElementById('lista-livros');
    ul.innerHTML = '';

    livros.forEach((livro, index) => {
        const li = document.createElement('li');
        li.innerHTML = `
            <span><strong>${livro.titulo}</strong> — ${livro.autor} <em>(${livro.categoria})</em></span>
        `;

        const btnEditar = document.createElement('button');
        btnEditar.textContent = 'Editar';
        btnEditar.onclick = () => editarLivro(index);

        const btnRemover = document.createElement('button');
        btnRemover.textContent = 'Remover';
        btnRemover.onclick = () => removerLivro(index);

        const acoes = document.createElement('div');
        acoes.appendChild(btnEditar);
        acoes.appendChild(btnRemover);

        li.appendChild(acoes);
        ul.appendChild(li);
    });
}

function limparFormularioLivro() {
    document.getElementById('input-titulo').value = '';
    document.getElementById('input-autor').value = '';
    document.getElementById('select-categoria').value = '';
}


document.addEventListener('DOMContentLoaded', () => {
    renderizarLivros();
});