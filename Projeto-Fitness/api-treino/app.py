from flask import Flask, request, jsonify
from pymongo import MongoClient
from bson.objectid import ObjectId
import requests
import os

app = Flask(__name__)

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/db_treinos")
API_USUARIOS_URL = os.getenv("API_USUARIOS_URL", "http://localhost:5001")
client = MongoClient(MONGO_URI)
db = client.get_database()
treinos_collection = db['treinos']

def validar_personal_headers():
    nome = request.headers.get('X-Nome')
    cpf = request.headers.get('X-Cpf')
    try:
        resp = requests.get(f"{API_USUARIOS_URL}/usuarios/validar?nome={nome}&cpf={cpf}")
        if resp.status_code == 200 and resp.json().get('cargo') == 'personal':
            return True
    except:
        pass
    return False

@app.route('/treinos', methods=['GET'])
def listar_treinos():
    nome = request.args.get('nome')
    cpf = request.args.get('cpf')
    
    resp = requests.get(f"{API_USUARIOS_URL}/usuarios/validar?nome={nome}&cpf={cpf}")
    if resp.status_code != 200:
        return jsonify({"erro": "Acesso negado. Forneça ?nome= e ?cpf= válidos."}), 401
        
    usuario = resp.json()
    
    treinos = []
    for t in treinos_collection.find():
        t['_id'] = str(t['_id'])
        
        if usuario['cargo'] == 'personal':
            treinos.append(t)
        elif usuario['cargo'] == 'aluno':
            atribuicoes = t.get('atribuicoes', [])
            if any(a['usuario_id'] == usuario['_id'] for a in atribuicoes):
                t['atribuicoes'] = [a for a in atribuicoes if a['usuario_id'] == usuario['_id']]
                treinos.append(t)
                
    return jsonify(treinos), 200

@app.route('/treinos', methods=['POST'])
def criar_treino():
    if not validar_personal_headers():
        return jsonify({"erro": "Acesso negado. Apenas personal pode criar treinos."}), 403
    
    data = request.get_json()
    novo_treino = {
        "nome": data.get('nome'),
        "exercicios": data.get('exercicios', []),
        "atribuicoes": []
    }
    resultado = treinos_collection.insert_one(novo_treino)
    return jsonify({"mensagem": "Treino criado", "id": str(resultado.inserted_id)}), 201

@app.route('/treinos/<id>', methods=['PUT', 'DELETE'])
def modificar_treino(id):
    if not validar_personal_headers():
        return jsonify({"erro": "Acesso negado."}), 403
        
    if request.method == 'PUT':
        resultado = treinos_collection.update_one({"_id": ObjectId(id)}, {"$set": request.get_json()})
        if resultado.matched_count == 0:
            return jsonify({"erro": "Treino não encontrado."}), 404
        return jsonify({"mensagem": "Treino atualizado"}), 200
    else:
        resultado = treinos_collection.delete_one({"_id": ObjectId(id)})
        if resultado.deleted_count == 0:
            return jsonify({"erro": "Treino não encontrado."}), 404
        return jsonify({"mensagem": "Treino removido"}), 200

@app.route('/treinos/<id>/atribuir', methods=['POST'])
def atribuir_aluno(id):
    if not validar_personal_headers():
        return jsonify({"erro": "Acesso negado."}), 403
        
    data = request.get_json()
    aluno_id = data.get('aluno_id')
    dias_semana = data.get('dias_semana', [])
    
    try:
        resp = requests.get(f"{API_USUARIOS_URL}/usuarios/id/{aluno_id}")
        if resp.status_code != 200 or resp.json().get('cargo') != 'aluno':
            return jsonify({"erro": "ID de Aluno inválido ou Inexistente."}), 400
    except:
        return jsonify({"erro": "Erro ao contatar API de Usuários."}), 500

    nova_atribuicao = {"usuario_id": aluno_id, "dias_semana": dias_semana}
    
    resultado = treinos_collection.update_one({"_id": ObjectId(id)}, {"$push": {"atribuicoes": nova_atribuicao}})
    if resultado.matched_count == 0:
        return jsonify({"erro": "ID do Treino não existe no banco de dados."}), 404
        
    return jsonify({"mensagem": "Aluno atribuído ao treino com sucesso!"}), 200

@app.route('/treinos/limpar_atribuicoes/<aluno_id>', methods=['DELETE'])
def limpar_atribuicoes(aluno_id):
    treinos_collection.update_many(
        {}, 
        {"$pull": {"atribuicoes": {"usuario_id": aluno_id}}}
    )
    return jsonify({"mensagem": "Limpeza concluída"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)