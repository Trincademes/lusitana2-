from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired, EqualTo, Length
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from datetime import datetime
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///modelo.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'meu_segredo'  # Defina um segredo para sessões
app.config['UPLOAD_FOLDER'] = 'static/uploads'  # Diretório para armazenar uploads

# Criação do diretório de uploads se não existir
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  # Rota de login

# Modelo do Usuário
class Usuario(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

# Função para carregar o usuário
@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))

# Formulário de Login
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])

# Formulário de Cadastro
class CadastroForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=100)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])

# Modelo de dados
class Modelo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.DateTime, nullable=False)
    hora = db.Column(db.Integer, nullable=False)  # Nova coluna para a hora
    minuto = db.Column(db.Integer, nullable=False)  # Nova coluna para o minuto
    apresentacao = db.Column(db.String(100), nullable=False)
    agendamento = db.Column(db.String(100), nullable=False)
    tipo_operacao = db.Column(db.String(100), nullable=False)
    numero_bs = db.Column(db.String(100), nullable=False)
    numero_nf = db.Column(db.String(100), nullable=False)
    transportadora = db.Column(db.String(100), nullable=False)
    tipo_veiculo = db.Column(db.String(100), nullable=False)
    cpf = db.Column(db.String(100), nullable=False)
    placa_cavalo = db.Column(db.String(100), nullable=False)
    placa_carreta = db.Column(db.String(100), nullable=False)
    numero_container = db.Column(db.String(100), nullable=False)
    documentos = db.Column(db.String(500), nullable=True)  # Armazena os nomes dos arquivos como uma string

# Rota para a página inicial (index)
@app.route('/')
def index():
    return render_template('index.html')

# Rota para login
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        usuario = Usuario.query.filter_by(username=form.username.data).first()
        if usuario and usuario.password == form.password.data:
            login_user(usuario)
            return redirect(url_for('home'))  # Redireciona para a página home após login
        else:
            flash('Login falhou. Verifique seu nome de usuário e senha.', 'danger')
    return render_template('login.html', form=form)

# Rota para cadastro
@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    form = CadastroForm()
    if form.validate_on_submit():
        usuario_existente = Usuario.query.filter_by(username=form.username.data).first()
        if usuario_existente:
            flash('Já existe uma conta com esse nome de usuário.', 'danger')
        else:
            novo_usuario = Usuario(username=form.username.data, password=form.password.data)
            db.session.add(novo_usuario)
            db.session.commit()
            flash('Cadastro realizado com sucesso!', 'success')
            return redirect(url_for('login'))
    return render_template('cadastro.html', form=form)

# Rota para a página home (exibir modelos cadastrados)
@app.route('/home')
@login_required
def home():
    modelos = Modelo.query.all()  # Exemplo: você pode querer listar todos os modelos
    return render_template('home.html', modelos=modelos)

# Rota para adicionar modelo
@app.route('/adicionar', methods=['GET', 'POST'])
@login_required  # Requer que o usuário esteja logado
def adicionar():
    if request.method == 'POST':
        documentos = request.files.getlist('documentos')
        document_names = []

        for doc in documentos:
            if doc:
                doc.save(os.path.join(app.config['UPLOAD_FOLDER'], doc.filename))
                document_names.append(doc.filename)

        novo_modelo = Modelo(
            data=datetime.strptime(request.form['data'], '%Y-%m-%d'),
            hora=request.form['hora'],
            minuto=request.form['minuto'],
            apresentacao=request.form['apresentacao'],
            agendamento=request.form['agendamento'],
            tipo_operacao=request.form['tipo_operacao'],
            numero_bs=request.form['numero_bs'],
            numero_nf=request.form['numero_nf'],
            transportadora=request.form['transportadora'],
            tipo_veiculo=request.form['tipo_veiculo'],
            cpf=request.form['cpf'],
            placa_cavalo=request.form['placa_cavalo'],
            placa_carreta=request.form['placa_carreta'],
            numero_container=request.form['numero_container'],
            documentos=','.join(document_names)
        )
        db.session.add(novo_modelo)
        db.session.commit()
        return redirect(url_for('home'))  # Redireciona para a página home após adicionar
    return render_template('adicionar.html')
# Rota para editar um modelo
@app.route('/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar(id):
    modelo = Modelo.query.get_or_404(id)  # Busca o modelo pelo ID ou retorna 404 se não encontrado
    if request.method == 'POST':
        # Atualize os dados do modelo com os dados do formulário
        modelo.data = datetime.strptime(request.form['data'], '%Y-%m-%d')
        modelo.hora = request.form['hora']
        modelo.minuto = request.form['minuto']
        modelo.apresentacao = request.form['apresentacao']
        modelo.agendamento = request.form['agendamento']
        modelo.tipo_operacao = request.form['tipo_operacao']
        modelo.numero_bs = request.form['numero_bs']
        modelo.numero_nf = request.form['numero_nf']
        modelo.transportadora = request.form['transportadora']
        modelo.tipo_veiculo = request.form['tipo_veiculo']
        modelo.cpf = request.form['cpf']
        modelo.placa_cavalo = request.form['placa_cavalo']
        modelo.placa_carreta = request.form['placa_carreta']
        modelo.numero_container = request.form['numero_container']
        
        # Atualização de documentos, se necessário
        documentos = request.files.getlist('documentos')
        document_names = []

        for doc in documentos:
            if doc:
                doc.save(os.path.join(app.config['UPLOAD_FOLDER'], doc.filename))
                document_names.append(doc.filename)

        modelo.documentos = ','.join(document_names)

        db.session.commit()
        flash('Modelo atualizado com sucesso!', 'success')
        return redirect(url_for('home'))  # Redireciona para a página home após editar
    return render_template('editar.html', modelo=modelo)


if __name__ == '__main__':
    app.run(debug=True)
