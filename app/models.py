from app import db, google_bp
from flask_login import UserMixin, current_user
from flask_dance.consumer.backend.sqla import OAuthConsumerMixin, \
        SQLAlchemyBackend

import datetime

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    avatar = db.Column(db.String(200))
    active = db.Column(db.Boolean, default=False)
    tokens = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default = datetime.datetime.utcnow())

    def __repr__(self):
        return '<User {}>'.format(self.name)

class OAuth(OAuthConsumerMixin, db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey(User.id))
    user = db.relationship(User)

google_bp.backend = SQLAlchemyBackend(OAuth, db.session, user=current_user)
