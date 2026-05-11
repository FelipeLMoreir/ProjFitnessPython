from flask import Flask, request, jsonify
from pymongo import MongoClient
from bson import ObjectId
import os
import requests

app = Flask(__name__)

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/db_usuarios")
client = MongoClient(MONGO_URI)
db = client.get_database()
usuarios_collection = db.usuarios

@app.route('/usuarios', methods=['POST'])
def criar_usuario():
    data = request.get_json()
    novo_usuario = {
        "nome": data.get('nome'),
        "idade": data.get('idade'),
        "email": data.get('email'),
        "cpf": data.get('cpf'),
        "cargo": data.get('cargo') 
    }
    resultado = usuarios_collection.insert_one(novo_usuario)
    return jsonify({"mensagem": "Usuário criado", "id": str(resultado.inserted_id)}), 201

@app.route('/usuarios', methods=['GET'])
def listar_usuarios():
    nome = request.args.get('nome')
    cpf = request.args.get('cpf')
    
    if not nome or not cpf:
        return jsonify({"erro": "Acesso negado. Forneça ?nome= e ?cpf= válidos na URL."}), 401
        
    usuarios = list(usuarios_collection.find())
    for u in usuarios:
        u['_id'] = str(u['_id'])
    return jsonify(usuarios), 200

@app.route('/usuarios/id/<id>', methods=['GET'])
def obter_usuario_por_id(id):
    usuario = usuarios_collection.find_one({"_id": ObjectId(id)})
    if usuario:
        usuario['_id'] = str(usuario['_id'])
        return jsonify(usuario), 200
    return jsonify({"erro": "Usuário não encontrado"}), 404

@app.route('/usuarios/<id>', methods=['PUT'])
def atualizar_usuario(id):
    data = request.get_json()
    resultado = usuarios_collection.update_one({"_id": ObjectId(id)}, {"$set": data})
    
    if resultado.matched_count == 0:
        return jsonify({"erro": "Usuário não encontrado"}), 404
        
    return jsonify({"mensagem": "Usuário atualizado com sucesso"}), 200

@app.route('/usuarios/<id>', methods=['DELETE'])
def deletar_usuario(id):
    resultado = usuarios_collection.delete_one({"_id": ObjectId(id)})
    
    if resultado.deleted_count == 0:
        return jsonify({"erro": "Usuário não encontrado"}), 404

    try:
        API_TREINO_URL = os.getenv("API_TREINO_URL", "http://api-treino:5000")
        requests.delete(f"{API_TREINO_URL}/treinos/limpar_atribuicoes/{id}")
    except Exception as e:
        print(f"Erro ao notificar API de Treinos: {e}")

    return jsonify({"mensagem": "Usuário removido e desvinculado"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)