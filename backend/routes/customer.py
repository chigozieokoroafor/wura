from flask import Blueprint, Response, jsonify, request
import pymongo
from backend.db import users, promotions_col,news_col
from backend.functions import Authentication, filter_cursor
from backend.config import secret_key
from werkzeug.security import generate_password_hash, check_password_hash
from pymongo.errors import DuplicateKeyError
import jwt, bson, datetime,random
from bson.errors import InvalidId



customer = Blueprint("customer", __name__)




@customer.route("/", methods=["GET"])
def h():
    data = jsonify(message="Welcome To Customer API")    
    return data


@customer.route("/createAccount", methods=["POST"])
def signup():
    info = request.json
    keys = [i for i in info.keys()]
    data = {}
    for i in keys:
        data[i] = info.get(i)
    try:
        email = data["email"]
        password = data["password"]
    except KeyError as e:
        return {"detail":f"{str(e)} field missing or empty", "status":"error"}, 400

    pwd_hashed = generate_password_hash(password, salt_length=32)
    data["pwd"] = pwd_hashed
    data["verified"] = False
    data["role"] = ["user"]
    otp_data = Authentication.generate_otp()
    data["otp_data"] = otp_data
    data["timestamp"] = datetime.datetime.now()
    data.pop("password")
    try :
        mail_send = Authentication.sendMail(email, otp_data["otp"])
        if mail_send["status"] == "success":
            users.insert_one(data)
        else:
            return jsonify({"detail":"Error occured while creating account","status":"fail"}), 400
        #users.find_one_and_update({"email":email}, {"$set":{"otp_data":otp_data}})
        
    except DuplicateKeyError as e:
        return jsonify({"detail":"Email address already used","status":"fail"}), 400
    return jsonify(detail="account created successfully", status="success", verified=False), 200
    
@customer.route("/emailCheck", methods=["POST"])
def emailCheck():
    email = request.json.get("email")

    email_check = users.find({"email":email}).hint("email_1")
    enail_list = list(email_check)
    if len(enail_list) > 0:
        message = jsonify({"detail":"Email address already used.", "status":"fail"}), 400
        return message
    message = jsonify({"detail":"Email address can be used.","status":"success"}),200
    return message

@customer.route("/signin", methods=["POST"])
def signin():
    info = request.json
    email = info.get("email")
    password = info.get("password")
    user_check = users.find({"email":email}).hint("email_1")
    user_list = list(user_check)
    if len(user_list) > 0 :
        user = user_list[0]
        pwd_check = check_password_hash(user["pwd"], password)
        if pwd_check:
            user["id"] = str(bson.ObjectId(user["_id"]))
            d = {"id": user["id"]}
            token = Authentication.generate_access_token(d)
            user["access_token"] = token
            user.pop("_id")
            user.pop("pwd")
            return jsonify({"detail":user, "status":"success"}), 200
        return jsonify({"detail":"Incorrect Details", "status":"fail"}), 401
        
    return jsonify({"detail": f"Account not found for {email}", "status":"fail"}), 404

@customer.route("/sendOTP", methods=["POST"])
def send_otp():
    email = request.json.get("email")
    email_check = users.find({"email":email}).hint("email_1")
    email_list = list(email_check)
    if len(email_list) > 0:
        otp_data = Authentication.generate_otp()
        users.find_one_and_update({"email":email}, {"$set":{"otp_data":otp_data}})
        mail_send = Authentication.sendMail(email, otp_data["otp"])
        if mail_send["status"]=="success":
            return jsonify({"detail":"OTP sent", "status":"success"}), 200
        else:
            return jsonify({"detail":"Error occured while sending mail","status":"fail"}),400

    return jsonify({"detail":"Account with provided email not found", "status":"error"}), 404

@customer.route("/emailVerification", methods=["POST"])
def email_verification():
    info = request.json
    email = info.get("email")
    otp = info.get("code")
    get_user = users.find({"email":email}).hint("email_1") #use the index created here
    user_list = list(get_user)
    if len(user_list)>0:
        user_check = user_list[0]
        now = datetime.datetime.timestamp(datetime.datetime.now())
        try:
            start_time = user_check["otp_data"]["starttime"]
            stop_time = user_check["otp_data"]["stoptime"]
        except KeyError as e:
            return jsonify({"detail":"OTP already used", "status":"error"}), 400
        otp_verify = False
        if stop_time > now > start_time :
            if otp == user_check["otp_data"]["otp"]:
                otp_verify = True
            else: return jsonify({"detail":"Invalid OTP provided", "status":"fail"}), 400
        else:
            return jsonify(message="OTP Expired", status="error"), 400
        
        if otp_verify == True:
            users.find_one_and_update({"email":email},{"$set":{"otp_data":{}, "verified":True}})
            data = {"email":email}
            jwt_token = Authentication.generate_access_token(data,1)
            return jsonify({"detail":"OTP Correct", "status":"success","token":jwt_token}), 200
            
    return jsonify({"detail":"Account with provided email not found", "status":"error"}), 404

@customer.route("/updatePassword", methods=["POST"])
@Authentication.token_required
def newPassword():
    token = request.headers.get("Authorization")
    data = jwt.decode(token, secret_key,algorithms=["HS256"])    
    new_password = request.json.get("newPassword")
    #data["newPassword"] = new_password
    try:
        email = data["email"]
    except KeyError as e:
        return jsonify({"detail":"Incorrect token provided", "status":"error"}), 401
    user_cursor = users.find({"email":email}).hint("email_1")
    user_list = list(user_cursor)
    user = user_list[0]
    choice_length = random.choice([16,32,64])
    new_hash = generate_password_hash(new_password,salt_length=choice_length)
    users.find_one_and_update({"_id":user["_id"]}, {"$set":{"pwd":new_hash}})
    
    return jsonify({"detail":"Password Updated Successfully", "status":"success"}), 200

@customer.route("/updateUserDetails", methods=["PUT"])
@Authentication.token_required
def updateDet():
    info = request.json
    data = {}
    keys = [i for i in info.keys()]
    for i in keys:
        data[i] = info.get(i)
    
    try:
        id = data["id"]
    except KeyError as e :
        return jsonify({"detail":"id parameter required","status":"fail"}),401

    try:
        for i in keys:
            if data[i] == "" or data["id"] == " ":
                data.pop(i)
        users.find_one_and_update({"_id":bson.ObjectId(id)}, {"$set":data})
        return jsonify({"detail":"User dertail uploaded", "status":"success"}), 200
    except InvalidId as e:
        return jsonify({"detail":"Invalid id value passed", "status":"error"}), 401


@customer.route("/home", methods=["GET"])
def home():
    if request.method == 'GET':
        promotion_cursor = promotions_col.find().sort("timestamp",pymongo.DESCENDING)
        promotion_list = filter_cursor(promotion_cursor)
        news_cursor = news_col.find().sort("timestamp",pymongo.DESCENDING)
        news = filter_cursor(news_cursor)
        
        data_object = {
            "promotions":promotion_list,
            "news":news,
            "new_products": [],
            "lucky_picks":[]
        }
        return jsonify(detail=data_object, status="success"), 200


@customer.route("/createRefreshToken",methods=["POST"])
def createRefresh():
    info = request.json
    id = info.get("id")
    #token = info.get("token")
    try:
        user_check = users.find_one({"_id":bson.ObjectId(id)})
    except InvalidId as e:
        return jsonify({"detail":"Invalid id passed", "status":"error"}), 401
    if user_check is not None:
        data = {"id":id,"role":user_check["role"]}
        token = Authentication.generate_access_token(data,1440)
        return jsonify({"detail":{"access_token":token}, "status":"success"}), 200
    return jsonify({"detail":"User not found","status":"error"}), 404

@customer.route("/test", methods=["GET"])
@Authentication.token_required #.token_required
def test():
    token = request.headers.get("Authorization")
    data = jwt.decode(token, secret_key,algorithms=["HS256"])
    # check if jwt token is expiring, generate a new one 
    return {"message":data}

