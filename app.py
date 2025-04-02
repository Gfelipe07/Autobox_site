from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

# Função para inicializar o banco de dados


def init_db():
    conn = sqlite3.connect('oficina.db')
    cursor = conn.cursor()

    # Criação das tabelas, caso não existam
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS clientes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        cpf TEXT NOT NULL,
        endereco TEXT NOT NULL,
        contato TEXT NOT NULL
    )''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS carros (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        marca TEXT NOT NULL,
        modelo TEXT NOT NULL,
        quilometragem TEXT NOT NULL,
        placa TEXT NOT NULL,
        cliente_id INTEGER,
        FOREIGN KEY (cliente_id) REFERENCES clientes(id)
    )''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS servicos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        descricao TEXT NOT NULL,
        carro_id INTEGER,
        cliente_id INTEGER,
        preco REAL NOT NULL,
        FOREIGN KEY (carro_id) REFERENCES carros(id),
        FOREIGN KEY (cliente_id) REFERENCES clientes(id)
    )''')

    conn.commit()
    conn.close()

# Função para adicionar coluna cliente_id se necessário


def adicionar_coluna_cliente_id():
    conn = sqlite3.connect('oficina.db')
    cursor = conn.cursor()
    try:
        cursor.execute('ALTER TABLE servicos ADD COLUMN cliente_id INTEGER;')
        conn.commit()
    except sqlite3.OperationalError:
        pass
    conn.close()

# Função para adicionar coluna preco se necessário


def adicionar_coluna_preco():
    conn = sqlite3.connect('oficina.db')
    cursor = conn.cursor()
    try:
        cursor.execute('ALTER TABLE servicos ADD COLUMN preco REAL NOT NULL;')
        conn.commit()
    except sqlite3.OperationalError:
        pass  # A coluna já existe
    conn.close()


# Inicializa o banco de dados
init_db()
adicionar_coluna_cliente_id()
adicionar_coluna_preco()


@app.route('/')
def index():
    conn = sqlite3.connect('oficina.db')
    cursor = conn.cursor()

    # Recupera todos os clientes
    cursor.execute('SELECT * FROM clientes')
    clientes = cursor.fetchall()

    # Recupera todos os carros
    cursor.execute('SELECT * FROM carros')
    carros = cursor.fetchall()

    # Recupera os serviços com os nomes dos carros e clientes usando LEFT JOIN
    cursor.execute('''
        SELECT s.id, s.descricao, s.preco,
               c.marca, c.modelo,
               cl.nome
        FROM servicos s
        LEFT JOIN carros c ON s.carro_id = c.id
        LEFT JOIN clientes cl ON s.cliente_id = cl.id
    ''')
    servicos_detalhados = cursor.fetchall()
    conn.close()
    return render_template('index.html', clientes=clientes, carros=carros, servicos=servicos_detalhados)


@app.route('/editar_cliente/<int:id>', methods=['GET', 'POST'])
def editar_cliente(id):
    conn = sqlite3.connect('oficina.db')
    cursor = conn.cursor()

    # Recupera os dados do cliente a ser editado
    cursor.execute('SELECT * FROM clientes WHERE id = ?', (id,))
    cliente = cursor.fetchone()

    if request.method == 'POST':
        nome = request.form['nome']
        cpf = request.form['cpf']
        endereco = request.form['endereco']
        contato = request.form['contato']

        cursor.execute('''
            UPDATE clientes SET nome = ?, cpf = ?, endereco = ?, contato = ?
            WHERE id = ?
        ''', (nome, cpf, endereco, contato, id))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))

    conn.close()
    return render_template('editar_cliente.html', cliente=cliente)


@app.route('/adicionar_cliente', methods=['GET', 'POST'])
def adicionar_cliente():
    if request.method == 'POST':
        nome = request.form['nome']
        cpf = request.form['cpf']
        endereco = request.form['endereco']
        contato = request.form['contato']

        conn = sqlite3.connect('oficina.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO clientes (nome, cpf, endereco, contato)
            VALUES (?, ?, ?, ?)
        ''', (nome, cpf, endereco, contato))
        conn.commit()
        conn.close()

        return redirect(url_for('index'))
    return render_template('adicionar_cliente.html')


@app.route('/adicionar_carro', methods=['GET', 'POST'])
def adicionar_carro():
    conn = sqlite3.connect('oficina.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, nome FROM clientes')
    clientes = cursor.fetchall()
    conn.close()

    if request.method == 'POST':
        marca = request.form['marca']
        modelo = request.form['modelo']
        quilometragem = request.form['quilometragem']
        placa = request.form['placa']
        cliente_id = request.form['cliente_id']

        conn = sqlite3.connect('oficina.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO carros (marca, modelo, quilometragem, placa, cliente_id)
            VALUES (?, ?, ?, ?, ?)
        ''', (marca, modelo, quilometragem, placa, cliente_id))
        conn.commit()
        conn.close()

        return redirect(url_for('index'))

    return render_template('adicionar_carro.html', clientes=clientes)


@app.route('/editar_carro/<int:id>', methods=['GET', 'POST'])
def editar_carro(id):
    conn = sqlite3.connect('oficina.db')
    cursor = conn.cursor()

    # Recupera os dados do carro a ser editado
    cursor.execute('SELECT * FROM carros WHERE id = ?', (id,))
    carro = cursor.fetchone()

    # Recupera todos os clientes para exibir no dropdown
    cursor.execute('SELECT id, nome FROM clientes')
    clientes = cursor.fetchall()
    conn.close()

    if request.method == 'POST':
        marca = request.form['marca']
        modelo = request.form['modelo']
        quilometragem = request.form['quilometragem']
        placa = request.form['placa']
        cliente_id = request.form['cliente_id']

        conn = sqlite3.connect('oficina.db')
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE carros SET marca = ?, modelo = ?, quilometragem = ?, placa = ?, cliente_id = ?
            WHERE id = ?
        ''', (marca, modelo, quilometragem, placa, cliente_id, id))
        conn.commit()
        conn.close()

        return redirect(url_for('index'))

    return render_template('editar_carro.html', carro=carro, clientes=clientes)


@app.route('/adicionar_servico', methods=['GET', 'POST'])
def adicionar_servico():
    conn = sqlite3.connect('oficina.db')
    cursor = conn.cursor()

    # Recupera todos os carros para exibir no dropdown
    cursor.execute('SELECT id, marca, modelo FROM carros')
    carros = cursor.fetchall()

    # Recupera todos os clientes para exibir no dropdown
    cursor.execute('SELECT id, nome FROM clientes')
    clientes = cursor.fetchall()
    conn.close()

    if request.method == 'POST':
        descricao = request.form['descricao']
        preco = (request.form['preco'])
        carro_id = request.form['carro_id']
        cliente_id = request.form['cliente_id']

        # Validação de preço
        if not preco or not preco.replace('.', '', 1).isdigit():
            return "Erro: Preço inválido ou não preenchido."

        try:
            preco = float(preco)  # Converte para float se válido
        except ValueError:
            return "Erro: Preço não é um número válido."

        # Inserção no banco de dados
        conn = sqlite3.connect('oficina.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO servicos (descricao, preco, carro_id, cliente_id)
            VALUES (?, ?, ?, ?)
        ''', (descricao, preco, carro_id, cliente_id))
        conn.commit()
        conn.close()

        return redirect(url_for('index'))

    return render_template('adicionar_servico.html', carros=carros, clientes=clientes)


@app.route('/editar_servico/<int:id>', methods=['GET', 'POST'])
def editar_servico(id):
    conn = sqlite3.connect('oficina.db')
    cursor = conn.cursor()

    # Recupera os dados do serviço a ser editado
    cursor.execute('SELECT * FROM servicos WHERE id = ?', (id,))
    servico = cursor.fetchone()

    if servico is None:
        conn.close()
        return "Serviço não encontrado!", 404

    # Recupera todos os carros
    cursor.execute('SELECT * FROM carros')
    carros = cursor.fetchall()

    # Recupera todos os clientes
    cursor.execute('SELECT id, nome FROM clientes')
    clientes = cursor.fetchall()

    conn.close()

    if request.method == 'POST':
        descricao = request.form['descricao']
        preco = request.form['preco']
        carro_id = request.form['carro_id']
        cliente_id = request.form['cliente_id']

        # Validação de preço
        if not preco or not preco.replace('.', '', 1).isdigit():
            return "Erro: Preço inválido ou não preenchido."

        try:
            preco = float(preco)  # Converte para float se válido
        except ValueError:
            return "Erro: Preço não é um número válido."

        # Se o preço for válido, insere no banco de dados
        conn = sqlite3.connect('oficina.db')
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE servicos SET descricao = ?, preco = ?, carro_id = ?, cliente_id = ?
            WHERE id = ?
        ''', (descricao, preco, carro_id, cliente_id, id))
        conn.commit()
        conn.close()

        return redirect(url_for('index'))

    return render_template('editar_servico.html', servico=servico, carros=carros, clientes=clientes)


@app.route('/excluir_cliente/<int:id>')
def excluir_cliente(id):
    conn = sqlite3.connect('oficina.db')
    cursor = conn.cursor()

    cursor.execute('DELETE FROM carros WHERE cliente_id = ?', (id,))
    cursor.execute('DELETE FROM servicos WHERE cliente_id = ?', (id,))
    cursor.execute('DELETE FROM clientes WHERE id = ?', (id,))
    conn.commit()
    conn.close()

    return redirect(url_for('index'))


@app.route('/deletar_carro/<int:id>')
def deletar_carro(id):
    conn = sqlite3.connect('oficina.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM carros WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))


@app.route('/excluir_servico/<int:id>')
def excluir_servico(id):
    conn = sqlite3.connect('oficina.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM servicos WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
