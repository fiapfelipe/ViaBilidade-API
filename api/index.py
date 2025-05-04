from flask import Flask, request, jsonify
from api.login import login
from api.manutencoes import manutencoes

app = Flask(__name__)

@app.route('/')
def home():
    return "Viabilidade - Use as rotas /login ou /manutencoes"

@app.route('/login', methods=['GET'])
def listar_usuarios():
    usuarios = [{'id': u['id'], 'username': u['username']} for u in login]
    return jsonify(usuarios), 200

@app.route('/login', methods=['POST'])
def fazer_login():
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

@app.route('/manutencoes', methods=['POST'])
def adicionar_manutencao():
    nova = request.get_json()
    nova['id'] = max(m['id'] for m in manutencoes) + 1 if manutencoes else 1
    nova['status'] = 'pendente'
    manutencoes.append(nova)
    return jsonify({'msg': 'Manutenção adicionada com sucesso'}), 201

@app.route('/manutencoes/<int:id>', methods=['PUT'])
def atualizar_status(id):
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

@app.route('/manutencoes/<int:id>', methods=['DELETE'])
def deletar_manutencao(id):
    for m in manutencoes:
        if m['id'] == id:
            manutencoes.remove(m)
            return jsonify({'msg': 'Manutenção excluída com sucesso'}), 200
    return jsonify({'msg': 'Manutenção não encontrada'}), 404