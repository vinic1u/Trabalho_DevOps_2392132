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
