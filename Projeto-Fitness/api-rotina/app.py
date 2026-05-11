from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

API_USUARIOS_URL = os.getenv("API_USUARIOS_URL", "http://localhost:5001")
API_TREINO_URL = os.getenv("API_TREINO_URL", "http://localhost:5002")

@app.route('/rotinas/usuario/<usuario_id>/dia/<dia>', methods=['GET'])
def buscar_treino_do_usuario_no_dia(usuario_id, dia):
    nome = request.args.get('nome')
    cpf = request.args.get('cpf')
    
    try:
        treinos_resp = requests.get(f"{API_TREINO_URL}/treinos?nome={nome}&cpf={cpf}")
        if treinos_resp.status_code != 200:
            return jsonify({"erro": "Credenciais inválidas ou sem permissão"}), 401
        treinos_data = treinos_resp.json()
    except:
        return jsonify({"erro": "Erro ao conectar com API de Treinos"}), 500

    treinos_do_dia = []
    for treino in treinos_data:
        for atribuicao in treino.get('atribuicoes', []):
            if atribuicao['usuario_id'] == usuario_id and dia in atribuicao['dias_semana']:
                treino_limpo = {k: v for k, v in treino.items() if k != 'atribuicoes'}
                treinos_do_dia.append(treino_limpo)

    if not treinos_do_dia:
        return jsonify({"mensagem": "Nenhum treino encontrado para este usuário neste dia."}), 404

    return jsonify({"usuario_id": usuario_id, "dia": dia, "treinos": treinos_do_dia}), 200


@app.route('/rotinas/treino/<treino_id>/dia/<dia>', methods=['GET'])
def buscar_usuarios_do_treino_no_dia(treino_id, dia):
    nome = request.args.get('nome')
    cpf = request.args.get('cpf')

    try:
        auth_resp = requests.get(f"{API_USUARIOS_URL}/usuarios/validar?nome={nome}&cpf={cpf}")
        if auth_resp.status_code != 200 or auth_resp.json().get('cargo') != 'personal':
            return jsonify({"erro": "Acesso restrito. Somente Personal pode ver esta lista."}), 403
    except:
        return jsonify({"erro": "Erro ao validar credenciais."}), 500

    try:
        treinos_resp = requests.get(f"{API_TREINO_URL}/treinos?nome={nome}&cpf={cpf}").json()
        usuarios_resp = requests.get(f"{API_USUARIOS_URL}/usuarios?nome={nome}&cpf={cpf}").json()
    except:
        return jsonify({"erro": "Erro de comunicação interna."}), 500

    treino_alvo = next((t for t in treinos_resp if t['_id'] == treino_id), None)
    if not treino_alvo:
        return jsonify({"erro": "Treino não encontrado."}), 404

    usuarios_no_dia = []
    for atribuicao in treino_alvo.get('atribuicoes', []):
        if dia in atribuicao['dias_semana']:
            user_info = next((u for u in usuarios_resp if u['_id'] == atribuicao['usuario_id']), None)
            if user_info:
                usuarios_no_dia.append({"id": user_info['_id'], "nome": user_info['nome']})

    if not usuarios_no_dia:
        return jsonify({"mensagem": "Nenhum usuário fará este treino neste dia."}), 404

    return jsonify({"treino_id": treino_id, "treino_nome": treino_alvo.get('nome'), "dia": dia, "alunos_inscritos": usuarios_no_dia}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)