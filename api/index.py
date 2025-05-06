from flask import Flask, request, jsonify
from flask_cors import CORS
from api.login import login
from api.manutencoes import manutencoes

app = Flask(__name__)
CORS(app, origins=["http://localhost:3000", "https://api-via-bilidade.vercel.app"])


@app.route('/')
def home():
    return "Viabilidade - Use as rotas /login ou /manutencoes"

@app.route('/login', methods=['GET'])
def listar_usuarios():
    usuarios = [{'id': u['id'], 'username': u['username']} for u in login]
    return jsonify(usuarios), 200

@app.route('/login', methods=['POST', 'OPTIONS'])
def fazer_login():
    if request.method == 'OPTIONS':
        return '', 200

    dados = request.get_json()
    username = dados.get('username')
    senha = dados.get('senha')

    for user in login:
        if user['username'] == username and user['senha'] == senha:
            return jsonify({'msg': 'Login bem-sucedido!'}), 200

    return jsonify({'msg': 'Usuário ou senha inválidos.'}), 401

@app.route('/manutencoes', methods=['GET'])
def listar_manutencoes():
    return jsonify(manutencoes), 200

@app.route('/manutencoes', methods=['POST', 'OPTIONS'])
def adicionar_manutencao():
    if request.method == 'OPTIONS':
        return '', 200

    nova = request.get_json()
    nova['id'] = max(m['id'] for m in manutencoes) + 1 if manutencoes else 1
    nova['status'] = 'pendente'
    manutencoes.append(nova)
    return jsonify({'msg': 'Manutenção adicionada com sucesso'}), 201

@app.route('/manutencoes/<int:id>', methods=['PUT', 'OPTIONS'])
def atualizar_status(id):
    if request.method == 'OPTIONS':
        return '', 200

    dados = request.get_json()
    novo_status = dados.get('status')

    if novo_status not in ['concluido', 'cancelado']:
        return jsonify({'msg': "Status inválido. Use 'concluido' ou 'cancelado'."}), 400

    for m in manutencoes:
        if m['id'] == id:
            if m['status'].lower() != 'pendente':
                return jsonify({'msg': 'Manutenção não pode ser atualizada. Já está concluída ou cancelada.'}), 400
            m['status'] = novo_status
            return jsonify({'msg': 'Status atualizado com sucesso'}), 200

    return jsonify({'msg': 'Manutenção não encontrada'}), 404

@app.route('/manutencoes/<int:id>', methods=['DELETE', 'OPTIONS'])
def deletar_manutencao(id):
    if request.method == 'OPTIONS':
        return '', 200

    for m in manutencoes:
        if m['id'] == id:
            manutencoes.remove(m)
            return jsonify({'msg': 'Manutenção excluída com sucesso'}), 200
    return jsonify({'msg': 'Manutenção não encontrada'}), 404
