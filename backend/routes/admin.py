from flask import Blueprint, jsonify, Response, request
import json

admin = Blueprint("admin", __name__)

@admin.route("/home", methods=["GET"])
def home():
    data = jsonify(message="This is home")
    return data