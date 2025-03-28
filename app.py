from flask import Flask, render_template, request, redirect
import sqlite3
from datetime import datetime

app = Flask(__name__)

DATABASE = 'clientes.db'


def conectar_banco():
    """Conecta ao banco de dados SQLite."""
    return sqlite3.connect(DATABASE)


def criar_tabelas():
    """Cria as tabelas 'clientes' e 'carros' se não existirem."""
    with conectar_banco() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS clientes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT,
                cpf TEXT,
                endereco TEXT,
                contato TEXT
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS carros (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                marca TEXT,
                modelo TEXT,
                quilometragem INTEGER,
                placa TEXT,
                cliente_id INTEGER,
                FOREIGN KEY (cliente_id) REFERENCES clientes (id)
            )
        ''')
        conn.commit()


criar_tabelas()


@app.route('/')
def index():
    """Exibe a lista de clientes e carros."""
    with conectar_banco() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM clientes')
        clientes = cursor.fetchall()
        cursor.execute('''
            SELECT carros.*, clientes.nome AS cliente_nome
            FROM carros
            JOIN clientes ON carros.cliente_id = clientes.id
        ''')
        carros = cursor.fetchall()
    return render_template('index.html', clientes=clientes, carros=carros, year=datetime.now().year)


@app.route('/adicionar_cliente', methods=['GET', 'POST'])
def adicionar_cliente():
    """Adiciona um novo cliente."""
    if request.method == 'POST':
        nome = request.form['nome']
        cpf = request.form['cpf']
        endereco = request.form['endereco']
        contato = request.form['contato']
        with conectar_banco() as conn:
            cursor = conn.cursor()
            cursor.execute('INSERT INTO clientes (nome, cpf, endereco, contato) VALUES (?, ?, ?, ?)',
                           (nome, cpf, endereco, contato))
            conn.commit()
        return redirect('/')
    return render_template('adicionar_cliente.html')


@app.route('/editar_cliente/<int:id>', methods=['GET', 'POST'])
def editar_cliente(id):
    """Edita um cliente existente."""
    with conectar_banco() as conn:
        cursor = conn.cursor()
        if request.method == 'POST':
            nome = request.form['nome']
            cpf = request.form['cpf']
            endereco = request.form['endereco']
            contato = request.form['contato']
            cursor.execute('UPDATE clientes SET nome = ?, cpf = ?, endereco = ?, contato = ? WHERE id = ?',
                           (nome, cpf, endereco, contato, id))
            conn.commit()
            return redirect('/')
        cursor.execute('SELECT * FROM clientes WHERE id = ?', (id,))
        cliente = cursor.fetchone()
    return render_template('editar_cliente.html', cliente=cliente)


@app.route('/deletar_cliente/<int:id>')
def deletar_cliente(id):
    """Deleta um cliente."""
    with conectar_banco() as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM clientes WHERE id = ?', (id,))
        conn.commit()
    return redirect('/')


@app.route('/adicionar_carro', methods=['GET', 'POST'])
def adicionar_carro():
    """Adiciona um novo carro."""
    with conectar_banco() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM clientes')
        clientes = cursor.fetchall()
        if request.method == 'POST':
            marca = request.form['marca']
            modelo = request.form['modelo']
            quilometragem = request.form['quilometragem']
            placa = request.form['placa']
            cliente_id = request.form['cliente_id']
            cursor.execute('INSERT INTO carros (marca, modelo, quilometragem, placa, cliente_id) VALUES (?, ?, ?, ?, ?)',
                           (marca, modelo, quilometragem, placa, cliente_id))
            conn.commit()
            return redirect('/')
    return render_template('adicionar_carro.html', clientes=clientes)


@app.route('/editar_carro/<int:id>', methods=['GET', 'POST'])
def editar_carro(id):
    """Edita um carro existente."""
    with conectar_banco() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM clientes')
        clientes = cursor.fetchall()
        if request.method == 'POST':
            marca = request.form['marca']
            modelo = request.form['modelo']
            quilometragem = request.form['quilometragem']
            placa = request.form['placa']
            cliente_id = request.form['cliente_id']
            cursor.execute('UPDATE carros SET marca = ?, modelo = ?, quilometragem = ?, placa = ?, cliente_id = ? WHERE id = ?',
                           (marca, modelo, quilometragem, placa, cliente_id, id))
            conn.commit()
            return redirect('/')
        cursor.execute('SELECT * FROM carros WHERE id = ?', (id,))
        carro = cursor.fetchone()
    return render_template('editar_carro.html', carro=carro, clientes=clientes)


@app.route('/deletar_carro/<int:id>')
def deletar_carro(id):
    """Deleta um carro."""
    with conectar_banco() as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM carros WHERE id = ?', (id,))
        conn.commit()
    return redirect('/')


if __name__ == '__main__':
    app.run(port=5001, debug=True)
