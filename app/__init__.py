import os
from flask import Flask, send_file
from config import Config

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS

app = Flask(__name__, 
        static_folder="../dist/static",
        template_folder='../dist')
app.config.from_object(Config)

db = SQLAlchemy(app)
migrate = Migrate(app, db)
cors = CORS(app,
        resources = {
            r"/api/*": {"origins": "*"}
            }
        )

app.secret_key = os.environ.get("FLASK_SECRET_KEY", "supersekrit")


from app import auth, models, util, youtube, chat
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    entry = os.path.join(app.config['DIST_DIR'], 'index.html')
    return send_file(entry)
