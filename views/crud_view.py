from typing import Union
from flask.views import MethodView
from flask import jsonify, request
from bson import ObjectId
from utils import serialize_doc
from pymongo.collection import Collection
from db import DB_Connection

class CRUDView(MethodView):
    collection_name = ''
    db = DB_Connection()
    
    @property
    def collection(self) -> Union[Collection, None]:
        this_collectioni = self.db.collections.get(self.collection_name)
        if this_collectioni is None:
            self.db.new_collection(self.collection_name)
            
        return self.db[self.collection_name]
    
    def get(self, object_id=None):
        if object_id:
            doc = self.collection.find_one({'_id': ObjectId(object_id)})
            if doc:
                return jsonify(serialize_doc(doc))
            return {'error': 'Document not found'}, 404
        else:
            docs = self.collection.find()
            return jsonify([serialize_doc(doc) for doc in docs])

    def post(self):
        data = request.json
        result = self.collection.insert_one(data)
        return jsonify({'_id': str(result.inserted_id)}), 201

    def put(self, object_id):
        data = request.json
        result = self.collection.update_one({'_id': ObjectId(object_id)}, {'$set': data})
        if result.matched_count:
            return {'success': True}
        return {'error': 'Document not found'}, 404

    def patch(self, object_id):
        data = request.json
        result = self.collection.update_one({'_id': ObjectId(object_id)}, {'$set': data})
        if result.matched_count:
            return {'success': True}
        return {'error': 'Document not found'}, 404

    def delete(self, object_id):
        result = self.collection.delete_one({'_id': ObjectId(object_id)})
        if result.deleted_count:
            return {'success': True}
        return {'error': 'Document not found'}, 404
