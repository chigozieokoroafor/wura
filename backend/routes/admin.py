from flask import Blueprint, jsonify, Response, request
import json
from werkzeug.security import check_password_hash, generate_password_hash
from backend.db import admin_col

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


@admin.route("/uploadProducts", methods=["POST","PUT", "GET"])
def upload_products():
    if request.method == "POST":
        return jsonify({"detail":"This is a post request"})
    if request.method == "PUT":
        return jsonify({"detail":"This is a PUT request"})
    else:
        return jsonify({"detail":f"{request.method} request not available"})