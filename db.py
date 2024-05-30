from pymongo import MongoClient
from  config import Config

conf = Config()
client = MongoClient(conf.MONGO_URI)
db = client[conf.DB_NAME]

# For testing
# client = MongoClient("mongodb://172.20.1.3:27017/")
# db = client.WorldGen

collections = {name: db[name] for name in db.list_collection_names() if name not in ['system.indexes', 'system.users']}
# for i,k in collections.items():
#     print(i)
#     for j in k.find():
#         print(j)
    