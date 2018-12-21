from app import db

import datetime

class User(db.Model): #{{{
    id = db.Column(db.Integer, primary_key=True)
    jwt_sub = db.Column(db.Integer, 
            unique=True, 
            nullable=False
    )
    last_action = db.Column(db.DateTime, default = datetime.datetime.utcnow())
    email = db.Column(db.String(256), unique=True, nullable=False)
    name = db.Column(db.String(256), nullable=False)
    avatar = db.Column(db.String(512))
    created_at = db.Column(db.DateTime, default = datetime.datetime.utcnow())
    oauth_creds = db.relationship('OAuthCreds', 
            uselist=False)

    def __repr__(self):
        return '<User {}>'.format(self.name)

#}}}
class OAuthCreds(db.Model): #{{{
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey(User.id), nullable=False) 
    user = db.relationship('User', uselist=False)
    token = db.Column(db.String(512), nullable=False)
    refresh_token = db.Column(db.String(512), nullable=False)
    token_uri = db.Column(db.String(512), nullable=False)
    client_id = db.Column(db.String(512), nullable=False)
    client_secret = db.Column(db.String(512), nullable=False)
    scopes = db.Column(db.String(512), nullable=False)

#}}}

# {{{ Chat Log Section
chatters_in_stream = db.Table('chatters_in_stream',
        db.Column('stream_id', db.Integer, db.ForeignKey('stream_log.id')),
        db.Column('chatter_id', db.Integer, db.ForeignKey('chatter_log.id'))
)
class Broadcaster(db.Model): # {{{
    id = db.Column(db.Integer, primary_key=True)

    channel_id = db.Column(db.String(512), nullable=False)
    channel_name = db.Column(db.String(64), nullable=False)
    avatar = db.Column(db.String(128), nullable=False)

    # Parent Relationships {{{
    streams = db.relationship('StreamLog', backref='streamer')
    # }}}

#}}}
class StreamLog(db.Model): #{{{
    id = db.Column(db.Integer, primary_key=True)

    video_id = db.Column(db.String(32), unique=True, nullable=False)
    video_title = db.Column(db.String(256), nullable=False)

    video_description = db.Column(db.String(1024), nullable=False)

    # {{{ Streams to Chatters Relationship
    '''
    Streams to Chatters is many-to-many relationship, reference the
    chatters_in_stream relationship table
    '''
    chatters = db.relationship('ChatterLog', 
            secondary=chatters_in_stream,
            backref=db.backref('stream', lazy='dynamic')
    ) # }}}
    # Parent Relationships {{{
    messages = db.relationship('MessageLog', backref='stream')
    #}}}
    # Child Relationships {{{
    streamer_id = db.Column(db.Integer, db.ForeignKey('broadcaster.id'))
    #}}}

#}}}
class ChatterLog(db.Model): #{{{
    id = db.Column(db.Integer, primary_key=True)

    author_channel_id = db.Column(db.String(512), nullable=False)
    author_name = db.Column(db.String(64), nullable=False)
    avatar = db.Column(db.String(128), nullable=False)

    # Parent Relationships {{{
    messages = db.relationship('MessageLog', backref='author')
    # }}}


#}}}
class MessageLog(db.Model): #{{{
    id = db.Column(db.Integer, primary_key=True)

    msg_id = db.Column(db.String(512), unique=True, nullable=False)
    text = db.Column(db.String(512), nullable=False)
    timestamp = db.Column(db.DateTime(), nullable=False)

    # Stream and Author information {{{
    stream_id = db.Column(db.Integer, db.ForeignKey('stream_log.id'))
    author_id = db.Column(db.Integer, db.ForeignKey('chatter_log.id'))
    #}}}
    # Relevant Author Tags {{{
    isMod = db.Column(db.Boolean())
    isOwner = db.Column(db.Boolean())
    isSponsor = db.Column(db.Boolean())
    #}}}

# }}}
# }}}
