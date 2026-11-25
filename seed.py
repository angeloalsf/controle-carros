"""Insere dados fictícios para demonstração. Execute: python seed.py"""
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from config import get_mongodb_uri

uri = get_mongodb_uri()
client = MongoClient(uri, serverSelectionTimeoutMS=10000)
db = client["controle_carros"]

db.carros.create_index("placa", unique=True)
db.proprietarios.create_index("cpf", unique=True)

if db.proprietarios.count_documents({}) == 0:
    owners = [
        {"nome": "João Silva", "cpf": "12345678900", "telefone": "(28) 99999-1111", "email": "joao@email.com"},
        {"nome": "Maria Oliveira", "cpf": "98765432100", "telefone": "(28) 98888-2222", "email": "maria@email.com"}
    ]
    db.proprietarios.insert_many(owners)

owners = list(db.proprietarios.find().sort("nome", 1))
if db.carros.count_documents({}) == 0 and owners:
    db.carros.insert_many([
        {"marca": "Toyota", "modelo": "Corolla", "ano": 2022, "cor": "Prata", "placa": "ABC1D23",
         "quilometragem": 35000, "combustivel": "Flex", "proprietario_id": owners[0]["_id"]},
        {"marca": "Honda", "modelo": "Civic", "ano": 2021, "cor": "Preto", "placa": "DEF4G56",
         "quilometragem": 48000, "combustivel": "Flex", "proprietario_id": owners[1]["_id"]},
        {"marca": "Volkswagen", "modelo": "Polo", "ano": 2023, "cor": "Branco", "placa": "GHI7J89",
         "quilometragem": 18000, "combustivel": "Flex", "proprietario_id": owners[0]["_id"]}
    ])

cars = list(db.carros.find().sort("placa", 1))
if db.manutencoes.count_documents({}) == 0 and cars:
    db.manutencoes.insert_many([
        {"carro_id": cars[0]["_id"], "tipo": "Troca de óleo", "descricao": "Troca de óleo e filtro",
         "data": "2026-10-15", "quilometragem": 33000, "valor": 250.0},
        {"carro_id": cars[1]["_id"], "tipo": "Pneus", "descricao": "Substituição de dois pneus",
         "data": "2026-11-02", "quilometragem": 47000, "valor": 900.0}
    ])

print("Dados de demonstração inseridos (ou já existentes).")
client.close()
