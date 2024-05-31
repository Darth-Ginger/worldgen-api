from typing import Union
from bson import ObjectId
from flask import json, jsonify
from pymongo import MongoClient, collection, IndexModel
from config import Config
from utils import serialize_doc, to_ObjectId

conf = Config()

class DB_Connection:
    URI = ""
    DB_NAME = ""
    client = MongoClient(URI)

    @property
    def collections(self):
        return {name: self.conn[name] for name in self.conn.list_collection_names() if name not in ['system.indexes', 'system.users']}
    
    @property
    def conn(self):
        return self.client[self.DB_NAME]
    
    def __init__(self, uri=conf.MONGO_URI, db_name=conf.DB_NAME):
        self.URI = uri
        self.DB_NAME = db_name
        for i in self.collections:
            self.create_name_index(i)
        
    def __del__(self):
        self.client.close()
        
    def __getitem__(self, collection_name: str) -> collection.Any:
        return self.collections[collection_name]

    def collection_exists(self, collection_name: str) -> bool:
        return collection_name in self.collections
    
    def new_collection(self, collection_name: str) -> collection:
        if not self.collection_exists(collection_name):
            self.conn.create_collection(collection_name)
            self.create_name_index(collection_name)
        return self.conn[collection_name]
    
    def collection_documents(self, collection_name: str) -> dict:
        docs = self.collections[collection_name].find({})
        for doc in docs:
            doc = serialize_doc(doc)
        return docs
    
    def collection_document_count(self, collection_name: str) -> int:
        return self.collections[collection_name].count_documents({})
    
    def collection_document(self, collection_name: str, object: Union[str, ObjectId]) -> Union[dict, None]:
        object_id = to_ObjectId(object)
        if to_ObjectId(object_id) is not None:
            doc = self.collections[collection_name].find_one({'_id': to_ObjectId(object_id)})
        else:
            raise ValueError('Invalid object id or Name')
        return serialize_doc(doc)
    
    def create_name_index(self, collection_name: str):
        collection = self.collections[collection_name]
        index_name = 'name_index'
        
        if collection.find({}).count() == 0 or \
            not collection.find_one({"Name": {"$exists": True}}) or \
            not collection.find_one({"name": {"$exists": True}}):
            return
        
        current_indexes = collection.list_indexes()
        for index in current_indexes:
            if index['name'] == index_name:
                return
        
        if collection.find_one({"Name": {"$exists": True}}):
            collection.create_index([('Name', 1)], name=index_name)
        else:
            collection.create_index([('name', 1)], name=index_name)