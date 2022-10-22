import pymongo

connection = pymongo.MongoClient("mongodb://backend:wurafadaka@54.221.70.10:27017")
#connection = pymongo.MongoClient()
db = connection["FADAKA"]
users = db["users"]
admin_col = db["admin"]
products = db["products"]
country = db["country_data"]
promotions_col = db["promotions"]
news_col = db["news"]

users.create_index("email", unique=True)
admin_col.create_index("email", unique=True)
admin_col.create_index("username", unique=True)
country.create_index("country", unique=True)
products.create_index("category")
#products.create_index([""])