import pymongo

connection = pymongo.MongoClient("mongodb://backend:wurafadaka@localhost")

db = connection["FADAKA"]
users = db["users"]
admin = db["admin"]
products = db["products"]
currency = db["country_data"]

users.create_index("email", unique=True)
admin.create_index("email", unique=True)
admin.create_index("username", unique=True)
