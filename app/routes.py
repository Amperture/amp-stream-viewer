#{{{ Python and Flask Imports
from app import app, db
from flask import redirect, url_for, jsonify, request

from app.util import auth_required, _credsToDict
from app.models import User, OAuthCreds, StreamLog, ChatterLog, MessageLog, \
        Broadcaster, chatters_in_stream

from sqlalchemy.orm.exc import NoResultFound, FlushError
from sqlalchemy.exc import IntegrityError
from sqlalchemy.dialects.postgresql import insert 
from sqlalchemy import desc 

import google_auth_oauthlib.flow
import google.oauth2.credentials

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2 import id_token
from google.auth.transport import requests

import datetime
import pytz
import pprint
import json
import os

#}}}

COMMON_ERRORS = { # {{{
        'backendError'      : "yt_backend_error",
        'liveChatEnded'     : 'chat_ended',
        'liveChatNotFound'  : 'chat_not_found',
        'liveChatDisabled'  : 'chat_disabled',
        }
# }}}

@app.route('/api/auth', methods=["POST"]) #{{{
def authUser():
    '''
    User Auth from API
    '''
    data = request.get_json()
    # {{{ Create OAuth Flow and Exchange Authorization Token for Refresh/Access
    try:
        flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
            app.config['CLIENT_SECRET_JSON_PATH'],
            scopes=[
                'https://www.googleapis.com/auth/userinfo.email', 
                'https://www.googleapis.com/auth/userinfo.profile', 
                'https://www.googleapis.com/auth/youtube.force-ssl',
                'https://www.googleapis.com/auth/youtube'])
        flow.redirect_uri = app.config['FRONTEND_URL']
        authorization_response = request.url
        flow.fetch_token(code=data['authCode'])
        credentials = flow.credentials
    except Exception as ex:
        print("Error exchanging tokens.", ex)
        return jsonify({
            'error' : 'Error exchanging authorization token.'
            }), 500

    #}}}

    #{{{ Use new OAuth Credentials to retrieve profile information
    try:
        # Grabbing the JWT 'sub' token.
        # Since the token is directly coming from Google via HTTPS, 
        # we can assume it's a legit id_token, and thus don't need to perform
        # a full validation.
        idInfo = id_token.verify_oauth2_token(
                credentials.id_token, 
                requests.Request(), 
                app.config['GOOGLE_OAUTH_CLIENT_ID']
        )
        gPlusAPIService = build('plus', 'v1', credentials=credentials)
        profile = gPlusAPIService.people().get(
                userId='me').execute() 
    except Exception as ex:
        print("Error retrieving profile: ", ex)
        return jsonify({
            'error' : 'Error retrieving profile information.'
            }, 500)
    #}}}

    #{{{ Update Profile Information, or Create New Profile
    email = idInfo['email']
    avatar = profile['image']['url']
    subToken = idInfo['sub']
    try:
        name = profile['displayName']
    except:
        name = email

    dbQuery = User.query.filter_by(jwt_sub = subToken)
    try:
        # Try to find existing user in database, if so update profile info.
        user = dbQuery.one()
        user.name = name
        user.avatar = avatar
        user.email = email

        OAuthCreds.query.filter_by(id = user.oauth_creds.id) \
            .update(_credsToDict(credentials))

        db.session.commit()
    except NoResultFound: 
        print('User with profile info not found, creating new user.')
        _createNewUser(subToken, profile, credentials)
    #}}}

    #{{{ Construct Data to Send back to the browser
    browserProfileData = {
            'user'  : {
                'name'   : name,
                'email'  : email,
                'avatar' : avatar
            },
            'token' : credentials.id_token
    }
    #}}}

    return jsonify(browserProfileData)

#}}}
@app.route('/api/auth', methods=["GET"]) #{{{
@auth_required
def auth_get(user): 
    '''
    Grab User Info from DB, requires JWT token as POST parameter.
    '''
    print("Trying to log user in")
    pprint.pprint(user)
    try:
        sendback = {
            'name' : user['user'].name,
            'email' : user['user'].email, 
            'avatar' : user['user'].avatar,
            'loggedIn' : True
        }
        return jsonify(sendback)
    except:
        return jsonify({
            'error' : 'unknown_error'
            }), 500
#}}}
@app.route('/googleauth', methods=["GET"]) #{{{
def googleAuth():
    '''
    Google OAuth Redirect
    '''
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        app.config['CLIENT_SECRET_JSON_PATH'],
        scopes=[
            'https://www.googleapis.com/auth/userinfo.email', 
            'https://www.googleapis.com/auth/userinfo.profile', 
            'https://www.googleapis.com/auth/youtube.force-ssl',
            'https://www.googleapis.com/auth/youtube'])
    flow.redirect_uri = app.config['FRONTEND_URL']
    authorization_url, state = flow.authorization_url(
            access_type='offline',
            #include_granted_scopes='true',
            #prompt='none%20consent'
            )

    return redirect(authorization_url, code=302)

#}}}
@app.route('/api/errortest', methods=["GET"]) #{{{
def errortest():
    '''
    Google OAuth Redirect
    '''
    return jsonify({
        'error' : 'test_error'
        }), 500

#}}}

def _createNewUser(subToken, profile, credentials):#{{{
    '''
    Create new Profile and Credentials entries in database.
    '''
    try: 
        name = profile['displayName']
    except:
        name = profile['emails'][0]['value']

    u = User(
        jwt_sub = subToken,
        email = profile['emails'][0]['value'],
        avatar = profile['image']['url'],
        name = name
    )
    c = OAuthCreds(user = u, **_credsToDict(credentials))
    db.session.add(u)
    db.session.add(c)
    db.session.commit()
    '''
    print("User ID: ", u.id)
    print("Creds ID: ", c.id)
    print("User Reference Token: ", u.oauth_creds.token)
    print("Creds Reference Email: ", c.user.email)
    '''


    return u
#}}}
