#{{{ Python and Flask Imports
from app import app, lm, db
from flask import redirect, url_for, jsonify, request, send_file

#from flask_dance.contrib.google import google
#from flask_dance.consumer import oauth_authorized

from flask_login import login_required, login_user, logout_user, current_user

from app.models import User, OAuthCreds

from sqlalchemy.orm.exc import NoResultFound

import google.oauth2.credentials
import google_auth_oauthlib.flow
from googleapiclient.discovery import build
from google.oauth2 import id_token
from google.auth.transport import requests

import pprint
import json
import os

#}}}

#{{{ Main Index Route. Render Webpage
@app.route('/', defaults={'path':''})
@app.route('/index', defaults={'path':''})
@app.route('/<path:path>')
def index(path):
    print(url_for('google.login'))
    dist_dir = app.config['DIST_DIR']
    index_path = os.path.join(dist_dir, 'index.html')
    return send_file(index_path)

#}}} 

#{{{ Stream List JSON
@app.route('/api/ytlivesearch', methods=["POST"])
def ytstreamlist():
    if google.authorized:
        print("yes")
    else: 
        print('no')
    form = request.form
    response = {}

    resp = google.get(
            '/youtube/v3/search?part=snippet&type=video&eventType=live&'
            'q=' + form['ytsearchterm'])

    print(resp.json())
    if resp.ok:
        lol = resp.json()
        return jsonify(lol)

#}}} 

#{{{ User Auth from API
@app.route('/api/auth', methods=["POST"])
def authUser():
    data = request.get_json()
    # {{{ Create OAuth Flow and Exchange Authorization Token for Refresh/Access
    try:
        flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
            app.config['CLIENT_SECRET_JSON_PATH'],
            scopes=['profile', 'email', 
                'https://www.googleapis.com/auth/youtube.force-ssl',
                'https://www.googleapis.com/auth/youtube'])
        flow.redirect_uri = "http://localhost:8080"
        authorization_response = request.url
        flow.fetch_token(code=data['authCode'])
        credentials = flow.credentials
        print("======== CREDENTIALS ==========")
        print(credentials.id_token)
        pprint.pprint(credentials)
        print("======== CREDENTIALS ==========")
    except Exception as ex:
        print("Error exchanging tokens.", ex)
        return jsonify({
            'error' : 'Error exchanging authorization token.'
            }, 500)

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
        #pprint.pprint(profile)
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
    print(browserProfileData)

    #}}}

    return jsonify(browserProfileData)

#}}}

#{{{ Making a Credentials object into a dictionary
def _credsToDict(credentials):
    return {
        'token' : credentials.token,
        'refresh_token' : credentials.refresh_token,
        'token_uri' : credentials.token_uri,
        'client_id' : credentials.client_id,
        'client_secret' : credentials.client_secret,
        'scopes' : str(credentials.scopes),
    }
#}}}

#{{{ Create new Profile and Credentials entries in database.
def _createNewUser(subToken, profile, credentials):
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
    print("User ID: ", u.id)
    print("Creds ID: ", c.id)
    print("User Reference Token: ", u.oauth_creds.token)
    print("Creds Reference Email: ", c.user.email)


    return "lol"
#}}}

#{{{ Logout Route
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

#}}}

#{{{ User Loader
@lm.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
