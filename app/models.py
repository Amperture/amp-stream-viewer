from app import db

import datetime

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    jwt_sub = db.Column(db.Integer, 
            unique=True, 
            nullable=False
    )
    email = db.Column(db.String(256), unique=True, nullable=False)
    name = db.Column(db.String(256), nullable=False)
    avatar = db.Column(db.String(512))
    created_at = db.Column(db.DateTime, default = datetime.datetime.utcnow())
    oauth_creds = db.relationship('OAuthCreds', 
            uselist=False)

    def __repr__(self):
        return '<User {}>'.format(self.name)

class OAuthCreds(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey(User.id), nullable=False) 
    user = db.relationship('User', uselist=False)
    token = db.Column(db.String(512), nullable=False)
    refresh_token = db.Column(db.String(512), nullable=False)
    token_uri = db.Column(db.String(512), nullable=False)
    client_id = db.Column(db.String(512), nullable=False)
    client_secret = db.Column(db.String(512), nullable=False)
    scopes = db.Column(db.String(512), nullable=False)

