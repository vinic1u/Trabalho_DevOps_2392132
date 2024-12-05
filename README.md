
# Trabalho DevOps

Objetivo: Implementar e configurar um ambiente completo de aplicação web com monitoramento e pipeline de CI/CD. Utilizar ferramentas como Jenkins, Prometheus e Grafana, configurando um fluxo automatizado desde o desenvolvimento até a visualização de métricas.

# Requisitos do Trabalho

#### 1. Configuração do Repositório Git
   - Crie um repositório chamado “Trabalho_DevOps_[RA]”.
   - Suba todos os arquivos de configuração utilizados no projeto (Dockerfiles, docker-compose.yml, arquivos do Prometheus e Grafana, Jenkinsfile).
   - Faça commits frequentes e mostre o progresso. Cada passo do trabalho deve ser documentado no repositório.

### 2. Implementação da Aplicação Web
   - Utilize a aplicação web desenvolvida em Flask, contendo um banco de dados MariaDB.
   - Adicione uma funcionalidade de cadastro de aluno. Esta funcionalidade deve ser simples e conter campos básicos como nome e RA.
   - Crie um arquivo de teste unitário para cadastrar um aluno e verificar se os dados foram armazenados corretamente no banco de dados.

### 3. Configuração da Pipeline no Jenkins
   - Configure o Jenkinsfile no repositório Git para automatizar o processo.
   - Estruture a pipeline em etapas:
     - Baixar código do Git: Jenkins deve clonar o repositório para iniciar o processo.
     - Rodar Testes: Jenkins deve rodar o teste criado para a aplicação web.
     - Build e Deploy: Jenkins deve realizar o build da aplicação, criar as imagens Docker, subir o ambiente completo e garantir que o monitoramento esteja funcionando.

### 4. Configuração do Monitoramento com Prometheus e Grafana
   - Prometheus: Configure o Prometheus para coletar métricas da aplicação web e do banco de dados MariaDB. 
   - Grafana: Crie uma dashboard no Grafana para visualizar as métricas da aplicação, incluindo o número de acessos à aplicação web e consultas ao banco de dados.
   - Inclua os arquivos de configuração do Grafana (datasources e dashboards) no repositório Git, garantindo que as dashboards sejam configuradas via arquivos de configuração.

### 5. Entrega Final
   - Certifique-se de que o ambiente está funcionando completamente: aplicação web, banco de dados, Prometheus, Grafana e Jenkins, com o monitoramento funcional, incluindo as dashboards ao subir o ambiente.
   - Enviar o link do repositório através do AVA para avaliação.

# Etapas para Execução da pipeline do projeto
- Abrir a URL do Jenkins (Geralmente Definido: http://localhost:8080/)
- Acessar com a conta definida
- Nova Tarefa
- Escolher pipeline
- Selecionar GIT no SCM
- Preencher no Repository URL: https://github.com/vinic1u/Trabalho_DevOps_2392132.git
- Selecioen a branch como **main**
- Salvar
- Construir agora para a execução da pipeline
- Caso os testes da aplicação PASSEM COM SUCESSO. A aplicação será executada normalmente e estará apta a ser utilizada.
# Etapas de Desenvolvimento do Projeto

 ### Criar um diretorio para o projeto
 ```bash
   mkdir nome_do_projeto
 ```
 ### Criar o arquivo do docker-compose
  ```bash
   nano docker-compose.yml
 ```
### Conteudo do docker-compose.yml
```yaml
version: '3.7'

services:
  flask:
    build:
      context: ./flask
      dockerfile: Dockerfile_flask
    ports:
      - "5000:5000"
    environment:
      - DATABASE_URL=mysql+pymysql://flask_user:flask_password@mariadb:3306/school_db
    depends_on:
      - mariadb

  mariadb:
    build:
      context: ./mariadb
      dockerfile: Dockerfile_mariadb
    ports:
      - "3306:3306"
    environment:
      MYSQL_ROOT_PASSWORD: root_password
      MYSQL_DATABASE: school_db
      MYSQL_USER: flask_user
      MYSQL_PASSWORD: flask_password

  test:
    build:
      context: ./flask
      dockerfile: Dockerfile_flask
    command: ["pytest", "/app/test_app.py"]
    depends_on:
      - mariadb
      - flask
    environment:
      - DATABASE_URL=mysql+pymysql://flask_user:flask_password@mariadb:3306/school_db
    networks:
      - default

  prometheus:
    image: prom/prometheus
    volumes:
      - ./prometheus/prometheus.yml:/etc/prometheus/prometheus.yml
    ports:
      - "9090:9090"
    depends_on:
      - mysqld_exporter
    command:
      - "--config.file=/etc/prometheus/prometheus.yml"

  mysqld_exporter:
    image: prom/mysqld-exporter
    ports:
      - "9104:9104"
    environment:
      DATA_SOURCE_NAME: "user:password@(mariadb:3306)/"
    depends_on:
      - mariadb

  grafana:
    build:
      context: ./grafana
      dockerfile: Dockerfile_grafana
    ports:
      - "3000:3000"
    depends_on:
      - prometheus
```
## Criar uma pasta nomeada flask e seguindo os seguintes procedimentos dentro dela
```
mkdir flask
```
### Criar o arquivo da aplicação flask **app.py**
```python
# Código principal do Flask (app.py)
import time
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_appbuilder import AppBuilder, SQLA
from flask_appbuilder.models.sqla.interface import SQLAInterface
from flask_appbuilder import ModelView
from sqlalchemy.exc import OperationalError
from prometheus_flask_exporter import PrometheusMetrics
import logging

app = Flask(__name__)

metrics = PrometheusMetrics(app)
# Configuração da chave secreta para sessões
app.config['SECRET_KEY'] = 'minha_chave_secreta_super_secreta'  # Substitua por uma chave segura

# Configuração do banco de dados
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:root_password@mariadb/school_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializar o banco de dados e o AppBuilder
db = SQLAlchemy(app)
appbuilder = AppBuilder(app, db.session)

# Configuração do log
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Modelo de Aluno - Definição da tabela 'Aluno' no banco de dados
class Aluno(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(50), nullable=False)
    sobrenome = db.Column(db.String(50), nullable=False)
    turma = db.Column(db.String(50), nullable=False)
    disciplinas = db.Column(db.String(200), nullable=False)
    ra = db.Column(db.String(200), nullable=False)


# Tentar conectar até o MariaDB estar pronto
attempts = 5
for i in range(attempts):
    try:
        with app.app_context():
            db.create_all()  # Inicializa o banco de dados
            # Criar um usuário administrador padrão
            if not appbuilder.sm.find_user(username='admin'):
                appbuilder.sm.add_user(
                    username='admin',
                    first_name='Admin',
                    last_name='User',
                    email='admin@admin.com',
                    role=appbuilder.sm.find_role(appbuilder.sm.auth_role_admin),
                    password='admin'
                )
        logger.info("Banco de dados inicializado com sucesso.")
        break
    except OperationalError:
        if i < attempts - 1:
            logger.warning("Tentativa de conexão com o banco de dados falhou. Tentando novamente em 5 segundos...")
            time.sleep(5)  # Aguarda 5 segundos antes de tentar novamente
        else:
            logger.error("Não foi possível conectar ao banco de dados após várias tentativas.")
            raise

# Visão do modelo Aluno para o painel administrativo
class AlunoModelView(ModelView):
    datamodel = SQLAInterface(Aluno)
    list_columns = ['id', 'nome', 'sobrenome', 'turma', 'disciplinas', 'ra']

# Adicionar a visão do modelo ao AppBuilder
appbuilder.add_view(
    AlunoModelView,
    "Lista de Alunos",
    icon="fa-folder-open-o",
    category="Alunos",
)

# Rota para listar todos os alunos - Método GET
@app.route('/alunos', methods=['GET'])
def listar_alunos():
    alunos = Aluno.query.all()
    output = [{'id': aluno.id, 'nome': aluno.nome, 'sobrenome': aluno.sobrenome, 'turma': aluno.turma, 'disciplinas': aluno.disciplinas, 'ra': aluno.ra} for aluno in alunos]
    return jsonify(output)

# Rota para adicionar um aluno - Método POST
@app.route('/alunos', methods=['POST'])
def adicionar_aluno():
    data = request.get_json()
    novo_aluno = Aluno(nome=data['nome'], sobrenome=data['sobrenome'], turma=data['turma'], disciplinas=data['disciplinas'], ra=data['ra'])
    db.session.add(novo_aluno)
    db.session.commit()
    logger.info(f"Aluno {data['nome']} {data['sobrenome']} adicionado com sucesso!")
    return jsonify({'message': 'Aluno adicionado com sucesso!'}), 201

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
```
**OBS: Certificar-se que o Modelo do Aluno esteja sendo criado antes de tentar a conexão com o banco para evitar erro de 'table doesn't exist'**

### Criar o arquivo para as depêndencias da aplicação
```txt
Flask==1.1.4  # Versão compatível com Flask-AppBuilder
Flask-SQLAlchemy==2.4.4  # Extensão do Flask para integração com SQLAlchemy
PyMySQL==0.9.3  # Biblioteca para conexão do Python com o banco de dados MariaDB
Flask-AppBuilder==3.3.0  # Versão compatível com Flask 1.x
Werkzeug==1.0.1  # Versão compatível do Werkzeug para evitar erros de importação
MarkupSafe==2.0.1  # Versão compatível com Jinja2 e Flask
WTForms==2.3.3  # Versão compatível com Flask-AppBuilder que contém o módulo 'compat'
prometheus-flask-exporter==0.18.3
pytest==6.2.5
pytest-flask==1.2.0
Flask-Testing==0.8.0
```

### Criação do DockerFile flask
```bash
# Dockerfile (Flask AppBuilder)
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

#COPY . .
COPY app.py /app/

# Copiar também o arquivo de teste test_app.py
COPY test_app.py /app/

CMD ["flask", "run", "--host=0.0.0.0"
```

### Criação do Arquivo para testes unitarios da aplicação flask

```python
import pytest
from flask import Flask
from flask.testing import FlaskClient

# Importar a aplicação Flask
from app import app  # Assumindo que seu arquivo principal é app.py

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

def test_listar_alunos(client: FlaskClient):
    """Testa a rota GET /alunos"""
    response = client.get('/alunos')
    assert response.status_code == 200
    assert isinstance(response.json, list)

def test_adicionar_aluno(client: FlaskClient):
    """Testa a rota POST /alunos"""
    new_aluno = {
        "nome": "Pedro Vinicius",
        "sobrenome": "Chagas Ribeiro",
        "turma": "4A",
        "disciplinas": "Programação Orientada a Objetos com Java 21",
        "ra": "23.9213-2"
    }
    response = client.post('/alunos', json=new_aluno)
    assert response.status_code == 201
    assert response.json['message'] == 'Aluno adicionado com sucesso!'
```

## Criar uma pasta nomeada mariadb e seguindo os seguintes procedimentos

```bash
mkdir mariadb
```

### Criar o Dockerfile do mariadb
```bash
# Dockerfile para MariaDB
# Salve este arquivo como Dockerfile.mariadb na raiz do projeto

# Dockerfile (MariaDB)
FROM mariadb:10.5

# Defina as variáveis de ambiente para o banco de dados
ENV MYSQL_ROOT_PASSWORD=root_password
ENV MYSQL_DATABASE=school_db
ENV MYSQL_USER=flask_user
ENV MYSQL_PASSWORD=flask_password

EXPOSE 3306
```

### Configuração do Prometheus e Grafana
Foram adicionado as pastas disponibilizadas pelo professor referente ao Prometheus e Grafana

### Criando o Dockerfile do grafana
```bash
FROM grafana/grafana:latest

USER root

# Criar os diretórios necessários
RUN mkdir /var/lib/grafana/dashboards

# Copiar os arquivos de provisionamento e dashboards
COPY provisioning/datasource.yml /etc/grafana/provisioning/datasources/
COPY provisioning/dashboard.yml /etc/grafana/provisioning/dashboards/
COPY dashboards/mariadb_dashboard.json /var/lib/grafana/dashboards/

# Ajustar permissões para o usuário grafana
RUN chown -R 472:472 /etc/grafana/provisioning

USER grafana
```

### Criando o Jenkinsfile para a pipeline conseguir ser executada

```bash
nano Jenkinsfile
```

### Apos a criação preencher o arquivo com a seguinte estrutura

```bash
pipeline {
    agent any

    stages {
        stage('Clonar Repositorio do Git e buildar os containers necessarios') {
            steps {
                script {
                    git branch: "main", url: "https://github.com/vinic1u/Trabalho_DevOps_2392132.git"
                    sh 'docker-compose down -v'
                    sh 'docker-compose build'
                }
            }
        }

        stage('Iniciar os containers e o Teste da aplicação') {
            steps {
                script {
                    sh 'docker-compose up -d mariadb flask test mysqld_exporter prometheus grafana'
                    sh 'sleep 40' 

                    try {
                        sh 'docker-compose run --rm test'
                    } catch (Exception e) {
                        currentBuild.result = 'FAILURE'
                        error "Testes da Aplicação Flask FALHARAM!!!. Pipipeline FINALIZADA"
                    }
                }
            }
        }

        stage('Manter a aplicação em execução') {
            steps {
                script {
                    sh 'docker-compose up -d mariadb flask test mysqld_exporter prometheus grafana'
                }
            }
        }
    }

    post {
        failure {
            sh 'docker-compose down -v'
        }
    }
}
```

