import os
dirbase = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    SECRET_KEY = os.environ.get("FLASK_SECRET_KEY") or 'try-and-guess-me'

    GOOGLE_OAUTH_CLIENT_ID = os.environ.get("GOOGLE_OAUTH_CLIENT_ID")
    GOOGLE_OAUTH_CLIENT_SECRET = os.environ.get("GOOGLE_OAUTH_CLIENT_SECRET")
    GOOGLE_OAUTH_REDIRECT_URI = os.environ.get("GOOGLE_OAUTH_REDIRECT_URI")
    GOOGLE_OAUTH_AUTH_URI = os.environ.get("GOOGLE_OAUTH_AUTH_URI")
    GOOGLE_OAUTH_TOKEN_URI = os.environ.get("GOOGLE_OAUTH_TOKEN_URI")

    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
            'sqlite:///' + os.path.join(dirbase, 'app.db')
    APP_DIR = os.path.dirname(__file__)
    DIST_DIR = os.path.join(APP_DIR, 'dist')
    CLIENT_SECRET_JSON_PATH = os.path.join(dirbase, 'client_secret.json')
    FRONTEND_URL = os.environ.get('FRONTEND_URL')
