import pymongo

connection = pymongo.MongoClient("mongodb://backend:wurafadaka@54.221.70.10:27017")
#connection = pymongo.MongoClient()
db = connection["FADAKA"]
users = db["users"]
admin_col = db["admin"]
products = db["products"]
country = db["country_data"]
promotions_col = db["promotions"]
image_folder_col = db["images_fol"]
image_col = db['images']
news_col = db["news"]

users.create_index("email", unique=True)
admin_col.create_index("email", unique=True)
admin_col.create_index("username", unique=True)
country.create_index("country", unique=True)
products.create_index("category")
#image_folder_col.create_index([('category', pymongo.ASCENDING)])
#image_col.create_index([('category', pymongo.ASCENDING)])
image_col.create_index([('parent_id', pymongo.ASCENDING)])
image_folder_col.create_index("name", unique=True)

#products.create_index([""])