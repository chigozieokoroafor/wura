import pymongo

connection = pymongo.MongoClient()

db = connection["FADAKA"]
users = db["users"]
admin = db["admin"]
products = db["products"]
currency = db["country_data"]

users.create_index("email", unique=True)
admin.create_index("email", unique=True)
admin.create_index("username", unique=True)
