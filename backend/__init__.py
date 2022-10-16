from random import random
from flask import Flask
from flask_cors import CORS
import string, random
from backend.routes.admin import admin
from backend.routes.customer import customer
from backend.routes.seller import merchant
from backend.config import secret_key


app = Flask(__name__)

app.config["SECRET_KEY"] = secret_key
#"".join(random.choices(string.ascii_letters, k=16))
CORS(app)

#configure thee blueprints here
app.register_blueprint(admin, url_prefix="/api/admin")
app.register_blueprint(customer, url_prefix="/api/customer")
app.register_blueprint(merchant, url_prefix="/api/merchant")

