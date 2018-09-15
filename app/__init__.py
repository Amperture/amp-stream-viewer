import os
from flask import Flask
from config import Config

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
#from flask_cors import CORS

from flask_dance.contrib.google import make_google_blueprint

app = Flask(__name__, static_folder="../dist/static")
app.config.from_object(Config)

db = SQLAlchemy(app)
migrate = Migrate(app, db)
lm = LoginManager(app)
#cors = CORS(app, resources={r"/*": {"origins": "*"}})
#cors = CORS(app)

app.secret_key = os.environ.get("FLASK_SECRET_KEY", "supersekrit")

google_bp = make_google_blueprint(
        scope=["profile", "email", 
        "https://www.googleapis.com/auth/youtube.force-ssl",
        "https://www.googleapis.com/auth/youtube"],
        offline=True
    )
app.register_blueprint(google_bp, url_prefix="/login")

from app import routes, models
