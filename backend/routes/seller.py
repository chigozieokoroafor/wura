from flask import Blueprint, jsonify, request

merchant = Blueprint("merchant", __name__)

@merchant.route("/home", methods=["GET"])
def home():
    data = jsonify(message="This is home")
    return data