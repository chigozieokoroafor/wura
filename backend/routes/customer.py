from flask import Blueprint, Response, jsonify, request
from backend.db import users
from backend.functions import Authentication
from backend.config import secret_key
from werkzeug.security import generate_password_hash, check_password_hash
from pymongo.errors import DuplicateKeyError
import jwt, bson, datetime
from functools import wraps
from jwt.exceptions import ExpiredSignatureError, DecodeError

customer = Blueprint("customer", __name__)


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        bearer_token = request.headers.get("Authorization")
        
        if not bearer_token:
            return jsonify({"message": "Token is missing"}), 403
        try:          
            data = jwt.decode(bearer_token, secret_key,algorithms=["HS256"])
        except ExpiredSignatureError as e:
            return jsonify({"message":"Token Expired", "status":"fail"}), 400
        except DecodeError as d:
            return jsonify({"message":"Incorrect Token", "status":"fail"}), 400
        return f(*args, **kwargs)
    return decorated


@customer.route("/home", methods=["GET"])
def home():
    data = jsonify(message="Welcome To Customer API")
    print()
    
    return data

@customer.route("/createAccount", methods=["POST"])
def signup():
    info = request.json
    keys = [i for i in info.keys()]
    data = {}
    for i in keys:
        data[i] = info.get(i)
    try:
        password = data["password"]
    except KeyError as e:
        return {"detail":"password field missing or empty", "status":"error"}, 400

    pwd_hashed = generate_password_hash(password, salt_length=32)
    data["pwd"] = pwd_hashed
    data["verified"] = False
    data.pop("password")
    try :
        users.insert_one(data)
    except DuplicateKeyError as e:
        return jsonify({"detail":"Email address already used","status":"fail"}), 400
    return jsonify(detail="account created successfully", status="success"), 200
    
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
        start_time = user_check["otp_data"]["starttime"]
        stop_time = user_check["otp_data"]["stoptime"]
        otp_verify = False
        if stop_time > now > start_time :
            if otp == user_check["otp_data"]["otp"]:
                otp_verify = True
            else: return jsonify({"detail":"Incorrect"}), 400
        else:
            return jsonify(message="OTP Expired", status="error", error_status=1), 400
        
        if otp_verify == True:
            users.find_one_and_update({"email":email},{"$set":{"otp_data":{}}})
            return jsonify({"detail":"OTP Correct", "status":"success"}), 200
            
    return jsonify({"detail":"Account with provided email not found", "status":"error"}), 404


    

@customer.route("/test", methods=["GET"])
@token_required
def test():
    token = request.headers.get("Authorization")
    data = jwt.decode(token, secret_key,algorithms=["HS256"])

    return {"message":data}

