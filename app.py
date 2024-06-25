from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

# Configuração do aplicativo Flask e do SQLAlchemy
app = Flask(__name__)
app.config['SECRET_KEY'] = 'sua_chave_secreta'  # Substitua pela sua chave secreta
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///C:/Users/Newton Hass Junior/PycharmProjects/luxury_wheels/static/Base_de_dados/Luxury_Whells.db'

db = SQLAlchemy(app)

# Definição do modelo de usuário (já existente)
class User(UserMixin, db.Model):
    __tablename__ = 'Clientes'
    id_cliente = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(150), unique=True, nullable=False)
    endereco = db.Column(db.String(150), nullable=False)
    telefone = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    senha = db.Column(db.String(150), nullable=False)

    def __init__(self, nome, endereco, telefone, email, senha):
        self.nome = nome
        self.endereco = endereco
        self.telefone = telefone
        self.email = email
        self.senha = senha  # Armazenar senha como texto simples

    def get_id(self):
        return str(self.id_cliente)

# Modelo para a tabela Veiculos (já existente)
class Veiculos(db.Model):
    __tablename__ = 'Veiculos'
    id_veiculo = db.Column(db.Integer, primary_key=True, autoincrement=True)
    marca = db.Column(db.String(100), nullable=False)
    modelo = db.Column(db.String(100), nullable=False)
    categoria = db.Column(db.String(100))
    transmissao = db.Column(db.String(100))
    tipo_veiculo = db.Column(db.String(100))
    quantidade_pessoas = db.Column(db.Integer)
    url_imagem = db.Column(db.String(200))
    valor_diaria = db.Column(db.Float)
    data_ultima_revisao = db.Column(db.Text)
    data_proxima_revisao = db.Column(db.Text)
    data_ultima_inspecao = db.Column(db.Text)

    def __init__(self, marca, modelo, categoria, transmissao, tipo_veiculo, quantidade_pessoas, url_imagem, valor_diaria, data_ultima_revisao, data_proxima_revisao, data_ultima_inspecao):
        self.marca = marca
        self.modelo = modelo
        self.categoria = categoria
        self.transmissao = transmissao
        self.tipo_veiculo = tipo_veiculo
        self.quantidade_pessoas = quantidade_pessoas
        self.url_imagem = url_imagem
        self.valor_diaria = valor_diaria
        self.data_ultima_revisao = data_ultima_revisao
        self.data_proxima_revisao = data_proxima_revisao
        self.data_ultima_inspecao = data_ultima_inspecao

# Modelo para a tabela Reservas (com ajuste na chave estrangeira)
class Reserva(db.Model):
    __tablename__ = 'Reservas'
    id_reserva = db.Column(db.Integer, primary_key=True)
    id_cliente = db.Column(db.Integer, db.ForeignKey('Clientes.id_cliente'), nullable=False)
    id_veiculo = db.Column(db.Integer, db.ForeignKey('Veiculos.id_veiculo'), nullable=False)
    data_inicio = db.Column(db.Text, nullable=False)
    data_fim = db.Column(db.Text, nullable=False)
    forma_pagamento = db.Column(db.Text)
    valor_total = db.Column(db.Float)

    def __init__(self, id_cliente, id_veiculo, data_inicio, data_fim, forma_pagamento=None, valor_total=None):
        self.id_cliente = id_cliente
        self.id_veiculo = id_veiculo
        self.data_inicio = data_inicio
        self.data_fim = data_fim
        self.forma_pagamento = forma_pagamento
        self.valor_total = valor_total

# Modelo para a tabela FormasPagamento
class FormasPagamento(db.Model):
    __tablename__ = 'FormasPagamento'
    id_forma_pagamento = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)

# Inicialização do LoginManager e definição da função load_user (já existente)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Rotas e funcionalidades

# Rota de index
@app.route('/')
def index():
    return render_template('index.html', on_index=True)

# Rota de cadastro (signup)
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        nome = request.form['username']
        endereco = request.form['endereco']
        telefone = request.form['telefone']
        email = request.form['email']
        senha = request.form['password']

        existing_user = User.query.filter_by(nome=nome).first()
        if existing_user:
            flash('Este nome de usuário já está em uso. Escolha outro.', 'error')
            return redirect(url_for('signup'))

        new_user = User(nome=nome, endereco=endereco, telefone=telefone, email=email, senha=senha)  # Armazenar senha como texto simples

        try:
            db.session.add(new_user)
            db.session.commit()
            flash('Cadastro realizado com sucesso! Faça login para continuar.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            print(e)
            flash('Ocorreu um erro ao cadastrar. Tente novamente.', 'error')

    return render_template('signup.html')

# Rota de login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        nome = request.form['username']
        senha = request.form['password']

        user = User.query.filter_by(nome=nome).first()

        if user:
            print(f'Tentativa de login com nome: {nome} e senha: {senha}')
            print(f'Senha armazenada no banco de dados para {nome}: {user.senha}')
            if user.senha == senha:  # Comparar senha diretamente
                login_user(user)
                flash('Login realizado com sucesso!', 'success')
                return redirect(url_for('dashboard'))  # Redireciona para o dashboard após login bem-sucedido
            else:
                flash('Senha incorreta. Tente novamente.', 'error')
        else:
            flash('Usuário não encontrado. Verifique seu nome de usuário.', 'error')

    return render_template('login.html')

# Rota de logout
@app.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    flash('Logout realizado com sucesso!', 'success')
    return redirect(url_for('index'))

# Rota do dashboard
@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', username=current_user.nome)

# Rota de pesquisa de veículos
@app.route('/search', methods=['GET', 'POST'])
@login_required
def search():
    if request.method == 'POST':
        categoria = request.form['categoria']
        transmissao = request.form['transmissao']
        tipo = request.form['tipo']
        valor_diaria = request.form['valor_diaria']
        capacidade_pessoas = request.form['capacidade_pessoas']

        # Construir a query base
        query = Veiculos.query

        # Aplicar os filtros apenas se algum campo estiver preenchido
        if categoria:
            query = query.filter(Veiculos.categoria == categoria)
        if transmissao:
            query = query.filter(Veiculos.transmissao == transmissao)
        if tipo:
            query = query.filter(Veiculos.tipo_veiculo == tipo)
        if valor_diaria:
            query = query.filter(Veiculos.valor_diaria <= float(valor_diaria))
        if capacidade_pessoas:
            query = query.filter(Veiculos.quantidade_pessoas == int(capacidade_pessoas))

        # Verifica se nenhum filtro foi aplicado
        if not (categoria or transmissao or tipo or valor_diaria or capacidade_pessoas):
            veiculos = Veiculos.query.all()  # Retorna todos os veículos

        # Executar a query
        veiculos = query.all()

        return render_template('search_results.html', veiculos=veiculos)

    return render_template('search.html')

# Exemplo de rota para realizar uma reserva
@app.route('/reservar', methods=['POST'])
@login_required
def reservar():
    if request.method == 'POST':
        id_veiculo = request.form['id_veiculo']
        data_inicio = request.form['data_inicio']
        data_fim = request.form['data_fim']
        valor_diaria = request.form['valor_diaria']
        forma_pagamento = request.form['forma_pagamento']  # Nova linha para capturar a forma de pagamento

        # Calcular o valor total da reserva
        inicio = datetime.strptime(data_inicio, '%Y-%m-%d')
        fim = datetime.strptime(data_fim, '%Y-%m-%d')
        diff_days = (fim - inicio).days
        valor_total = float(valor_diaria) * diff_days

        # Salvar a reserva no banco de dados
        nova_reserva = Reserva(
            id_cliente=current_user.id_cliente,
            id_veiculo=int(id_veiculo),
            data_inicio=data_inicio,
            data_fim=data_fim,
            forma_pagamento=forma_pagamento,  # Incluindo a forma de pagamento na reserva
            valor_total=valor_total
        )

        try:
            db.session.add(nova_reserva)
            db.session.commit()
            flash('Reserva realizada com sucesso!', 'success')
            return redirect(url_for('dashboard'))
        except Exception as e:
            print(e)
            flash('Erro ao processar a reserva. Tente novamente.', 'error')

    return redirect(url_for('index'))

# Rota para exibir reservas do usuário
@app.route('/minhas_reservas')
@login_required
def minhas_reservas():
    reservas = Reserva.query.filter_by(id_cliente=current_user.id_cliente).all()
    return render_template('minhas_reservas.html', reservas=reservas)

# Rota para cancelar uma reserva
@app.route('/cancelar_reserva/<int:id_reserva>', methods=['POST'])
@login_required
def cancelar_reserva(id_reserva):
    reserva = Reserva.query.get(id_reserva)

    if reserva:
        try:
            db.session.delete(reserva)
            db.session.commit()
            flash('Reserva cancelada com sucesso!', 'success')
        except Exception as e:
            print(e)
            flash('Erro ao cancelar a reserva. Tente novamente.', 'error')

    return redirect(url_for('minhas_reservas'))

if __name__ == '__main__':
    app.run(debug=True)
