import os
from flask import Flask
from config import Config

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager # Unnecessary?
from flask_cors import CORS

app = Flask(__name__, static_folder="../dist/static")
app.config.from_object(Config)

db = SQLAlchemy(app)
migrate = Migrate(app, db)
lm = LoginManager(app) # Unnecessary?
cors = CORS(app)

app.secret_key = os.environ.get("FLASK_SECRET_KEY", "supersekrit")

from app import routes, models
