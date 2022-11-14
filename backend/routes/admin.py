from datetime import datetime
from bson import ObjectId
from bson.errors import InvalidId
from flask import Blueprint, jsonify, Response, request
import json,jwt
from pymongo.errors import DuplicateKeyError
from bson.errors import InvalidId
from backend.config import secret_key
from werkzeug.security import check_password_hash, generate_password_hash
from backend.db import admin_col, promotions_col,news_col, image_folder_col, image_col
from backend.functions import Authentication, filter_cursor
import random


admin = Blueprint("admin", __name__)

@admin.route("/home", methods=["GET"])
def home():
    data = jsonify(message="This is the Admin test endpoint")
    return data

@admin.route("/createAccount",methods=["POST"])
def createAccount():
    info = request.json
    keys = [i for i in info.keys()]

    data = {}
    for i in keys:
        data[i] = info.get(i)
    
    try:
        email = data["email"]
        password = data["password"]
    except KeyError as e:
        return jsonify({"detail":f"{e} field is required","status":"fail"}), 400
    
    hashed_password = generate_password_hash(password,salt_length=64)
    data.pop("password")
    data["pwd"] = hashed_password
    data["verified"] = False
    data["role"] = ["admin"]
    admin_col.insert_one(data)
    return jsonify({"detail":"account created","status":"success"}), 200

@admin.route("/signin", methods=["POST"])
def signin():
    info = request.json
    email = info.get("email")
    password = info.get("password")
    
    user_check = admin_col.find_one({"email":email}) #.hint("email_1")
    if user_check is not None:    
        pwd = user_check["pwd"]
        pwd_check = check_password_hash(pwd, password)
        if pwd_check == True:
            user_check["id"] = str(ObjectId(user_check["_id"]))
            user_check.pop("_id")
            return jsonify(detail=user_check, status="success"), 200
        return jsonify({"detail":"Incorrect password", "status":"fail"}), 403
    return jsonify({"detail":"User Not found", "status":"error"}), 403

@admin.route("/uploadProducts", methods=["POST","PUT", "GET", "DELETE"])
@Authentication.token_required
def upload_products():
    if request.method == "POST":
        return jsonify({"detail":"This is a post request"})
    if request.method == "PUT":
        return jsonify({"detail":"This is a PUT request"})
    else:
        return jsonify({"detail":f"{request.method} request not available"})

    

@admin.route("/promotions", methods=["POST", "PUT", "DELETE", "GET"])
@Authentication.token_required
#create admin check
def updatePromotions():

    token = request.headers.get("Authorization")
    decoded_data = jwt.decode(token, secret_key,["HS256"])
    if request.method == "GET":
        args = request.args
        page = args.get("page")

        try:
            user_role = decoded_data["role"]
        except KeyError as e:
            return jsonify({"detail":"Unauthorized Access", "status":"error"}), 401

        if "admin" in user_role:
            try:
                offset = 5
                skip = int(page) * offset
            except TypeError as e:
                return jsonify({"detail":"page argument required.", "status":"error"}), 401
            except ValueError as e:
                return jsonify({"detail":"Integer value required.", "status":"error"}), 401

            promotions_cursor = promotions_col.find().skip(skip).limit(offset)
            promotions_list = list(promotions_cursor)
            #print(promotions_list)
            promotions = []
            if len(promotions_list) > 0:
                for i in promotions_list:
                    i["id"] = str(ObjectId(i["_id"]))
                    i.pop("_id")
                    promotions.append(i)
            #t = Authentication.generate_refresh_token(token)
            return jsonify(detail=promotions, status="success"), 200
        return jsonify({"detail":"Unauthorized Access", "status":"error"}), 401

    if request.method =="POST":
        
        try:
            user_role = decoded_data["role"]
        except KeyError as e:
            return jsonify({"detail":"Unauthorized access", "status":"error"}), 401
        if "admin" in user_role:
            info = request.json
            keys = [i for i in info.keys()]
            data = {}
            for i in keys:
                data[i] = info.get(i)
            data["timestamp"] = datetime.timestamp(datetime.now())
            promotions_col.insert_one(data)
            return jsonify({"detail":"Promotion uploaded.", "status":"success"}), 200
        return jsonify({"detail":"Unauthorized access","status":"error"}), 401
            
            
    if request.method =="PUT":
        try:
            user_role = decoded_data["role"]
        except KeyError as e:
            return jsonify({"detail":"Unauthorized access", "status":"error"}), 401
        if "admin" in user_role:
            info =request.json
            keys = [i for i in info.keys()]
            data = {}
            for i in keys:
                data[i]= info.get(i)
            
            try:
                id = data["id"]
            except KeyError as e:
                return jsonify({"detail": f"{e} key not provided."}),401
            for i in keys:
                if data[i] == "":
                    data.pop(i)
            try:        
                data.pop("id")
            except KeyError as e:
                return jsonify({"detail":"id parameter cannot be empty","status":"fail"}),401
            data["timestamp"] = datetime.timestamp(datetime.now())
            try:
                promotions_col.find_one_and_update({"_id":ObjectId(id)}, {"$set": data})        
            except InvalidId as e :
                return jsonify({"detail":"Invalid id passed", "status":"error"}), 403

            return jsonify({"detail":"Promotion data updated", "status":"success"}),404
        return jsonify({"detail":"Unauthorized Access","status":"fail"}), 401
        
    if request.method =="DELETE":
        id = request.args.get("id")
        try:
            user_role = decoded_data["role"]
        except KeyError as e:
            return jsonify({"detail":"Unauthorized access", "status":"error"}), 401
        if "admin" in user_role:
            promotions_col.delete_one({"_id":ObjectId(id)})
            return jsonify({"details":"Promotion data deleted","status":"success"}), 200
        return jsonify({"detail":"Unauthorized Access","status":"fail"}), 401



@admin.route("/news", methods=["POST", "PUT", "DELETE", "GET"])
@Authentication.token_required
#create admin check
def news_route():

    token = request.headers.get("Authorization")
    decoded_data = jwt.decode(token, secret_key,["HS256"])
    if request.method == "GET":
        args = request.args
        page = args.get("page")

        try:
            user_role = decoded_data["role"]
        except KeyError as e:
            return jsonify({"detail":"Unauthorized Access", "status":"error"}), 401

        if "admin" in user_role:
            try:
                offset = 5
                skip = int(page) * offset
            except TypeError as e:
                return jsonify({"detail":"page argument required.", "status":"error"}), 401
            except ValueError as e:
                return jsonify({"detail":"Integer value required.", "status":"error"}), 401

            news_cursor = news_col.find().skip(skip).limit(offset)
            news_list = list(news_cursor)
            news = []
            if len(news_list) > 0:
                for i in news_list:
                    i["id"] = str(ObjectId(i["_id"]))
                    i.pop("_id")
                    news.append(i)
            #t = Authentication.generate_refresh_token(token)
            return jsonify(detail=news, status="success"), 200
        return jsonify({"detail":"Unauthorized Access", "status":"error"}), 401

    if request.method =="POST":
        
        try:
            user_role = decoded_data["role"]
        except KeyError as e:
            return jsonify({"detail":"Unauthorized access", "status":"error"}), 401
        if "admin" in user_role:
            info = request.json
            keys = [i for i in info.keys()]
            data = {}
            for i in keys:
                data[i] = info.get(i)
            data["timestamp"] = datetime.timestamp(datetime.now())
            news_col.insert_one(data)
            return jsonify({"detail":"News uploaded.", "status":"success"}), 200
        return jsonify({"detail":"Unauthorized access","status":"error"}), 401
            
            
    if request.method =="PUT":
        try:
            user_role = decoded_data["role"]
        except KeyError as e:
            return jsonify({"detail":"Unauthorized access", "status":"error"}), 401
        if "admin" in user_role:
            info =request.json
            keys = [i for i in info.keys()]
            data = {}
            for i in keys:
                data[i]= info.get(i)
            
            try:
                id = data["id"]
            except KeyError as e:
                return jsonify({"detail": f"{e} key not provided."}),401
            for i in keys:
                if data[i] == "":
                    data.pop(i)
            try:        
                data.pop("id")
            except KeyError as e:
                return jsonify({"detail":"id parameter cannot be empty","status":"fail"}),401
            data["timestamp"] = datetime.timestamp(datetime.now())
            try:
                news_col.find_one_and_update({"_id":ObjectId(id)}, {"$set": data})        
            except InvalidId as e:
                return jsonify({"detail":"Invalid Id passed", "status":"error"}), 403

            return jsonify({"detail":"Promotion data updated", "status":"success"}),200
        return jsonify({"detail":"Unauthorized Access","status":"fail"}), 401
        
    if request.method =="DELETE":
        id = request.args.get("id")
        try:
            user_role = decoded_data["role"]
        except KeyError as e:
            return jsonify({"detail":"Unauthorized access", "status":"error"}), 401
        if "admin" in user_role:
            news_col.delete_one({"_id":ObjectId(id)})
            return jsonify({"details":"Promotion data deleted","status":"success"}), 200
        return jsonify({"detail":"Unauthorized Access","status":"fail"}), 401


#for base folders
@admin.route("/gallery", methods=['POST', "PUT", "DELETE", "GET"])
@Authentication.token_required
def base():
    token = request.headers.get("Authorization")
    decoded_data = jwt.decode(token, secret_key,["HS256"])
    if request.method == 'POST':
        try:
            user_role = decoded_data["role"]
        except KeyError as e:
            return jsonify({"detail":"Unauthorized access", "status":"error"}), 401
        
        if "admin" in user_role:
            info = request.json
            keys = [i for i in info.keys()]
            data = {}
            for i in keys:
                data[i] = info.get(i)
            try:
                url = data["image_url"]
                name = data["name"]
                #category = data['category']
            except KeyError as E:
                return jsonify({"detail":f'{E}  required', "status":"fail"}), 400
            data["timestamp_created"] = datetime.timestamp(datetime.now())
            data["timestamp_updated"] = datetime.timestamp(datetime.now())
            data["parent_id"] =  ""
            data["isFolder"] = True
            data['category'] = ""
            try:
                image_folder_col.insert_one(data)
            except DuplicateKeyError as e:
                error = e.details
                #return jsonify({"detail":f"folder with {e.args} exists"}), 400
                error_keys = error["keyValue"].keys()
                error_list = []
                for i in error_keys:
                    string = f'folder with {i} "{error["keyValue"][i]}" exists'
                    error_list.append(string)

                return jsonify(detail=error_list, status='error'), 400
            return ({"detail":"Image Folder Created", 'status':"success"}), 200
        return jsonify({"detail":"Unauthorized Access", "status":"error"}), 401
        

    if request.method == 'GET':
        try:
            user_role = decoded_data["role"]
        except KeyError as e:
            return jsonify({"detail":"Unauthorized access", "status":"error"}), 401
        if "admin" in user_role:
            page = request.args.get("page")
            try:
                offset = 30
                skip = int(page*offset)
            except Exception as e:
                skip = 0
            q_data = {"isFolder":True, "parent_id":""}
            images_cursor = image_folder_col.find(q_data).skip(skip)
            images = list(i for i in images_cursor)
            for i in images:
                i["id"] = str(ObjectId(i["_id"]))
                i.pop("_id")
            return jsonify(detail=images, status="success"), 200
            
                     
    if request.method == 'PUT':
        try:
            user_role = decoded_data["role"]
        except KeyError as e:
            return jsonify({"detail":"Unauthorized access", "status":"error"}), 401
        
        if "admin" in user_role:
            info = request.json
            keys = [i for i in info.keys()]
            data = {}
            for i in keys:
                data[i] = info.get(i)
            
            try:
                id  = data["id"]
                data.pop("id")
            except KeyError as e:
                return jsonify({"detail":f"{e} is required to update item","status":"fail"}), 400
            for i in data.keys():
                if data[i] == "":
                    data.pop(i)
            data["timestamp_updated"] = datetime.timestamp(datetime.now())
            item_Check = image_folder_col.find_one({"_id":ObjectId(id)})
            if item_Check == None:
                return jsonify({"detail":"item with id not found", "status":"fail"}), 400
            try:
                image_folder_col.find_one_and_update({"_id":ObjectId(id)}, {"$set":data})
            except InvalidId as e:
                return jsonify({"detail":f"'id' passed is not valid", "status":"error"}), 400
            updated_item = image_folder_col.find_one({"_id":ObjectId(id)})
            updated_item["id"] = str(ObjectId(updated_item["_id"]))
            updated_item.pop("_id")
            return jsonify({"detail":updated_item, "status":"success"}), 200
            
            
    if request.method == 'DELETE':
        id = request.args.get("id")
        image_folder_col.delete_one({"_id":ObjectId(id)})
        image_col.delete_many({"parent_id":id})
        return jsonify({"detail":"item deleted", "status":"success"}), 200


#for navigating into folders
@admin.route("/gallery/<folder_id>", methods=['POST', "PUT", "DELETE", "GET"])
@Authentication.token_required
def images_route(folder_id):
    token = request.headers.get("Authorization")
    decoded_data = jwt.decode(token, secret_key,["HS256"])
    if request.method == 'POST':
        try:
            user_role = decoded_data["role"]
        except KeyError as e:
            return jsonify({"detail":"Unauthorized access", "status":"error"}), 401
        if "admin" in user_role:
            info = request.json
            keys = [i for i in info.keys()]
            data = {}
            for i in keys:
                data[i] = info.get(i)
            
            folder_check = image_folder_col.find_one({"_id":ObjectId(folder_id)})
            if folder_check == None:
                return jsonify({"detail":"Folder non-existent", "status":"fail"}), 400
            try:
                url = data["image_url"]
                name = data["name"]
                #category = data['category']
            except KeyError as E:
                return jsonify({"detail":f'{E}  required', "status":"fail"}), 400

            data["timestamp_created"] = datetime.timestamp(datetime.now())
            data["timestamp_updated"] = datetime.timestamp(datetime.now())
            data['parent_id'] = folder_id
            image_col.insert_one(data)
            
            return ({"detail":"Image Document Uploaded", 'status':"success"}), 200
        return jsonify({"detail":"Unauthorized Access", "status":"error"}), 401
        

    if request.method == 'GET':
        try:
            user_role = decoded_data["role"]
        except KeyError as e:
            return jsonify({"detail":"Unauthorized access", "status":"error"}), 401
        if "admin" in user_role:
            page = request.args.get("page")
            try:
                offset = 30
                skip = int(page*offset)
            except Exception as e:
                skip = 0
            images_cursor = image_col.find({"parent_id":folder_id}).skip(skip)
            image_list = list(i for i in images_cursor)

            for i in image_list:
                i["id"] = str(ObjectId(i["_id"]))
                i.pop("_id")
            x = random.choices(image_list,k=len(image_list))
            return jsonify({"detail":x, "status":"success"}), 200
        return jsonify({"detail":"Unauthorized Access", "status":"error"}), 401
            
            
    if request.method == "PUT":
        try:
            user_role = decoded_data["role"]
        except KeyError as e:
            return jsonify({"detail":"Unauthorized access", "status":"error"}), 401        
        if "admin" in user_role:
            info = request.json
            keys = [i for i in info.keys()]
            data = {}
            for i in keys:
                data[i] = info.get(i)
                
            try:
                id  = data["id"]
                data.pop("id")
            except KeyError as e:
                return jsonify({"detail":f"{e} is required to update item","status":"fail"}), 400
            for i in data.keys():
                if data[i] == "":
                    data.pop(i)
            folder_check = image_folder_col.find_one({"_id":ObjectId(folder_id)})
            if folder_check == None:
                return jsonify({"detail":f"image folder with id {folder_id} not found", "status":"fail"}), 400
            data["timestamp_updated"] = datetime.timestamp(datetime.now())
            item_Check = image_col.find_one({"_id":ObjectId(id)})
            if item_Check == None:
                return jsonify({"detail":"item with id not found", "status":"fail"}), 400
            try:
                image_col.find_one_and_update({"_id":ObjectId(id)}, {"$set":data})
            except InvalidId as e:
                return jsonify({"detail":f"'id' passed is not valid", "status":"error"}), 400
            updated_item = image_col.find_one({"_id":ObjectId(id)})
            updated_item["id"] = str(ObjectId(updated_item["_id"]))
            updated_item.pop("_id")
            return jsonify({"detail":updated_item, "status":"success"}), 200
                
            
    if request.method == 'DELETE':
        id = request.args.get("id")
        image_col.delete_one({"_id":ObjectId(id)})
        return jsonify({"detail":"item deleted", "status":"success"}), 200


@admin.route("/createRefreshToken",methods=["POST"])
#@Authentication.token_required
def createRefresh():
    info = request.json
    id = info.get("id")
    #token = info.get("token")
    try:
        user_check = admin_col.find_one({"_id":ObjectId(id)})
    except InvalidId as e:
        return jsonify({"detail":"Invalid id passed", "status":"error"}), 401
    if user_check is not None:
        data = {"id":id,"role":user_check["role"]}
        token = Authentication.generate_access_token(data,1440)
        user_check["access_token"] = token
        user_check.pop("_id")
        user_check.pop("pwd")
        #user_check.pop("otp_data")
        return jsonify({"detail":user_check, "status":"success"}), 200
    return jsonify({"detail":"User not found","status":"error"}), 404
