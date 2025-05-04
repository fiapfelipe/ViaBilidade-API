from flask import Flask, request, jsonify
import oracledb
import secrets

app = Flask(__name__)

# Função para conectar ao banco Oracle
def conectar():
    return oracledb.connect(
        user="rm559175",
        password="fiap25",
        dsn="oracle.fiap.com.br/orcl"
    )

# Rota para listar todos os logins (GET)
@app.route('/login', methods=['GET'])
def listar_logins():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT username, password FROM loginviabilidade")
    colunas = [col[0].lower() for col in cursor.description]
    resultados = [dict(zip(colunas, row)) for row in cursor.fetchall()]
    cursor.close()
    conn.close()
    return jsonify(resultados)

# Rota para realizar o login (POST)
@app.route('/login', methods=['POST'])
def login():
    dados = request.get_json()
    username = dados.get('username')
    password = dados.get('password')

    if not username or not password:
        return jsonify({"msg": "Username e password são obrigatórios."}), 400

    # Conectar ao banco de dados e verificar se o login existe
    conn = conectar()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT COUNT(*) FROM loginviabilidade WHERE username = :1 AND password = :2
    """, (username, password))

    resultado = cursor.fetchone()
    cursor.close()
    conn.close()

    # Verifica se existe um login válido
    if resultado[0] > 0:
        return jsonify({"msg": "Login bem-sucedido!"}), 200
    else:
        return jsonify({"msg": "Usuário ou senha inválidos."}), 401

if __name__ == '__main__':
    app.run(debug=True)

# Rota para listar todas as manutenções
@app.route('/manutencoes', methods=['GET'])
def listar_manutencoes():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT id, componente, descricao, trem, setor, status FROM manutencoes")
    colunas = [col[0].lower() for col in cursor.description]
    resultados = [dict(zip(colunas, row)) for row in cursor.fetchall()]
    cursor.close()
    conn.close()
    return jsonify(resultados)

# Rota para adicionar uma nova manutenção
@app.route('/manutencoes', methods=['POST'])
def adicionar_manutencao():
    dados = request.get_json()
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO manutencoes (componente, descricao, trem, setor, status)
        VALUES (:1, :2, :3, :4, 'pendente')
    """, (dados['componente'], dados['descricao'], dados['trem'], dados['setor']))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"msg": "Manutenção adicionada com sucesso"}), 201

# Rota para atualizar o status de uma manutenção
@app.route('/manutencoes/<int:id>', methods=['PUT'])
def atualizar_manutencao(id):
    dados = request.get_json()
    novo_status = dados.get('status')

    # Verifica se o status é válido
    if novo_status not in ['concluido', 'cancelado']:
        return jsonify({"msg": "Status inválido. Apenas 'concluído' ou 'cancelado' são permitidos."}), 400

    conn = conectar()
    cursor = conn.cursor()

    # Verifica se a manutenção existe e se está com status 'pendente'
    cursor.execute("SELECT status FROM manutencoes WHERE id = :1", [id])
    manutencao = cursor.fetchone()

    if not manutencao:
        cursor.close()
        conn.close()
        return jsonify({"msg": "Manutenção não encontrada"}), 404

    if manutencao[0] != 'pendente':
        cursor.close()
        conn.close()
        return jsonify({"msg": "A manutenção não pode ser alterada, pois não está com status 'pendente'."}), 400

    # Atualiza o status da manutenção
    cursor.execute("""
        UPDATE manutencoes
        SET status = :1
        WHERE id = :2
    """, (novo_status, id))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"msg": f"Status da manutenção alterado para '{novo_status}' com sucesso!"})

# Rota para excluir uma manutenção
@app.route('/manutencoes/<int:id>', methods=['DELETE'])
def excluir_manutencao(id):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM manutencoes WHERE id = :1", [id])
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"msg": "Manutenção excluída com sucesso"})

if __name__ == '__main__':
    app.run(debug=True)
