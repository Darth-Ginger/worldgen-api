import re
from typing import Union
from bson import ObjectId
from pymongo import MongoClient, collection
from pymongo.collection import Collection
from config import Config
from utils import serialize_doc

conf = Config()

class DB_Connection:
    URI = ""
    DB_NAME = ""
    CLIENT = None

    @property
    def collections(self):
        """
        Returns a dictionary of collections in the database, excluding system collections.
        :return: A dictionary where the keys are collection names and the values are pymongo Collection objects.
        :rtype: dict
        """
        return {name: self.conn[name] for name in self.conn.list_collection_names() if name not in ['system.indexes', 'system.users']}
    
    @property
    def conn(self):
        """
        Returns a connection to the MongoDB database specified by `self.DB_NAME`.
        :return: A pymongo.database.Database object representing the database connection.
        """
        return self.CLIENT[self.DB_NAME]
    
    def __init__(self, uri=conf.MONGO_URI, db_name=conf.DB_NAME):
        """
        Initializes a new instance of the class.

        Parameters:
            uri (str): The URI of the MongoDB server. Defaults to the value specified in the conf module.
            db_name (str): The name of the MongoDB database. Defaults to the value specified in the conf module.

        Returns:
            None
        """
        self.DB_NAME = db_name
        self.URI = uri
        self.CLIENT = MongoClient(self.URI)
        for i in self.collections:
            self.create_name_index(i)
        
    def __del__(self):
        self.CLIENT.close()
        
    def __getitem__(self, collection_name: str) -> collection.Any:
        """
        Get an item from the collections dictionary by its collection name.

        Parameters:
            collection_name (str): The name of the collection to retrieve.

        Returns:
            collection.Any: The collection object corresponding to the given name.
        """
        return self.collections[collection_name]

    def collection_exists(self, collection_name: str) -> bool:
        """
        Check if a collection with the given name exists.

        Parameters:
            collection_name (str): The name of the collection to check.

        Returns:
            bool: True if the collection exists, False otherwise.
        """
        return collection_name in self.collections
    
    def new_collection(self, collection_name: str) -> Union[Collection, None]:
        """
        Creates a new collection in the MongoDB database with the given name if it does not already exist.

        :param collection_name: A string representing the name of the collection to be created.
        :type collection_name: str
        :return: A pymongo.collection.Collection object representing the newly created collection if it was created successfully.
                 None if a collection with the given name already exists.
        :rtype: Union[pymongo.collection.Collection, None]
        """
        if self.collection_exists(collection_name):
            return None
        self.conn.create_collection(collection_name)
        self.create_name_index(collection_name)
        return self.conn[collection_name]
    
    def all_collection_documents(self, collection_name: str) -> list[dict]:
        """
        Retrieves all documents from the specified collection.

        Args:
            collection_name (str): The name of the collection to retrieve documents from.

        Returns:
            List[dict]: A list of dictionaries containing the retrieved documents.
                        If the collection is empty, an empty list is returned.
        """
        documents = list(self.collections[collection_name].find())
        return [serialize_doc(doc) for doc in documents]
    
    def collection_document_count(self, collection_name: str) -> int:
        return self.collections[collection_name].count_documents({})
    
    def collection_document(self, collection_name: str, object: Union[str, ObjectId]) -> Union[dict, None]:
        """
        Retrieves a document from the specified collection based on the provided object ID.

        Args:
            collection_name (str): The name of the collection to retrieve the document from.
            object (Union[str, ObjectId]): The object ID or name of the document to retrieve.

        Returns:
            Union[dict, None]: The serialized document as a dictionary, or None if the document does not exist.

        Raises:
            ValueError: If the provided object ID or name is invalid.
        """
        object_id = self.to_ObjectId(object)
        if self.to_ObjectId(object_id) is not None:
            doc = self.collections[collection_name].find_one({'_id': self.to_ObjectId(object_id)})
        else:
            raise ValueError('Invalid object id or Name')
        return serialize_doc(doc)
    
    def create_name_index(self, collection_name: str):
        """
        Creates a name index for the specified collection.

        Args:
            collection_name (str): The name of the collection to create the name index for.

        Returns:
            None: If the collection is empty or does not contain any documents with the 'Name' or 'name' field.

        Raises:
            None
        """
        collection = self.collections[collection_name]
        index_name = 'name_index'
        
        if self.collection_document_count(collection_name) == 0 or \
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
    
    def to_ObjectId(self, obj: Union[ObjectId, str]) -> Union[ObjectId, None]:
        """
        Converts the given object to a MongoDB ObjectId.

        Parameters:
            obj (Union[ObjectId, str]): 
                - The object to convert. 
                    - Can be an existing ObjectId, 
                        a string representation of an ObjectId, 
                        or a string representing a World Name to be converted to an ObjectId.

        Returns:
            Union[ObjectId, None]: 
                - The converted ObjectId if the conversion is successful. 
                - Returns None if the conversion fails.

        Raises:
            None

        Examples:
            >>> db = DB_Connection()
            >>> db.to_ObjectId("5f7b16423d8d4400043dc49a")
            ObjectId('5f7b16423d8d4400043dc49a')
            >>> db.to_ObjectId(ObjectId("5f7b16423d8d4400043dc49a"))
            ObjectId('5f7b16423d8d4400043dc49a')
            >>> db.to_ObjectId("A World Name")
            ObjectId('5f7b16423d8d4400043dc49a')
            >>> db.to_ObjectId("invalid_id")
            None
        """
        objectid_pattern = re.compile(r'^[0-9a-fA-F]{24}$')
        if isinstance(obj, ObjectId):
            return obj
        elif re.match(objectid_pattern, obj):
            return ObjectId(obj)
        else:
            world = self.collections["Worlds"].find_one({"WorldName": obj})
            if world is not None:
                return world["_id"]
            return None
        
    def upsert_object(collection: collection, obj: dict) -> Union[ObjectId, None]:
        """
        Insert or update an object in the specified collection.

        :param collection: The MongoDB collection.
        :param obj: The object to insert or update.
        :return: The _id of the inserted or updated object.
        """
        if '_id' in obj and obj['_id']:
            obj_id = obj['_id']
            del obj['_id']
            result = collection.update_one({'_id': ObjectId(obj_id)}, {'$set': obj}, upsert=True)
            if result.upserted_id is not None:
                return result.upserted_id
            else:
                return ObjectId(obj_id)
        else:
            result = collection.insert_one(obj)
            return result.inserted_id