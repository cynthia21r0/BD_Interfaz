from pymongo import MongoClient


def get_client():
    """Retorna el cliente de MongoDB (conexión local por defecto)."""
    return MongoClient("mongodb://localhost:27017/")


def get_collection(db_name: str, collection_name: str):
    """Retorna la colección indicada de la base de datos indicada."""
    client = get_client()
    db = client[db_name]
    return db[collection_name]