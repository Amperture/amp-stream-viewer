# Imports {{{
from app import app, db
from flask import request, jsonify

from app.models import User, OAuthCreds, StreamLog, ChatterLog, MessageLog, \
        Broadcaster, chatters_in_stream

from functools import wraps

import google_auth_oauthlib.flow
import google.oauth2.credentials

from google.oauth2 import id_token
from google.auth.transport import requests

import time

import datetime
# }}}

@app.route('/api/errortest', methods=["GET"]) #{{{
def errortest():
    '''
    Google OAuth Redirect
    '''
    return jsonify({
        'error' : 'test_error'
        }), 500

#}}}

def refresh_jwt(jwt, idInfo, credsDBEntry):#{{{

    '''
    Compare the expiration timestamp of the jwt token,
    if the token expires in less than fifteen minutes, renew it.
    '''
    credentials = _dbToCreds(credsDBEntry)
    now = datetime.datetime.now()
    exp = datetime.datetime.fromtimestamp(idInfo['exp'])
    delta = exp - now
    if(delta <= datetime.timedelta(minutes=15)):
        credentials.refresh(requests.Request())
        return credentials.id_token

    return jwt

#}}}
def function_timer(func): # {{{

    @wraps(func)
    def timed_function(*args, **kwargs):
        now = time.time()
        result = func(*args, **kwargs)
        later = time.time()
        execute_time = later - now

        print("That operation took {}.".format(execute_time))
        return result

    return timed_function

# }}}
def auth_required(func):#{{{

    '''
    Authorization Function for all Protected Routes.
    Mark any route that requires authorization with `@auth_required`
    '''
    @wraps(func)
    def _auth(*args, **kwargs):
        # Verify Token Was Sent {{{

        try:
            jwt = request.headers['Authorization']
        except KeyError:
            return jsonify({
                'detail' : 'No Authorization Token Provided',
                'error' : 'invalid_token'
                }), 401

        # }}} 
        # Verify Token Comes from Google and hasn't expired {{{

        try:
            idInfo = id_token.verify_oauth2_token(
                    jwt, 
                    requests.Request(), 
                    app.config['GOOGLE_OAUTH_CLIENT_ID']
            )

            if idInfo['iss'] not in ['accounts.google.com', 
                    'https://accounts.google.com']:
                return jsonify({
                    'error' : 'Wrong Issuer'
                    }), 401
            
        except Exception as ex:
            print("Error Verifying Token: ", ex)
            return jsonify({
                'error' : 'Unknown Error Verifying Token'
                }), 401

        # }}}
        # Verify User Exists in Database {{{

        try:
            dbQuery = User.query.filter_by(jwt_sub = idInfo['sub'])
            user = dbQuery.one()
        except Exception as ex:
            print("Error Finding User: ", ex)
            return jsonify({
                'error' : 'Unknown Error Finding User'
                }), 401

        #}}}
        # Refresh JWT Token if Needed {{{
        credentials = _dbToCreds(user.oauth_creds)
        
        jwt = refresh_jwt(jwt, idInfo, user.oauth_creds)
        # }}}
        # Execute Wrapped Route Function {{{
        userDict = {
                'user'          : user,
                'credentials'   : credentials,
                'jwt'           : jwt 
                }
        return func(userDict, *args, **kwargs)
        # }}}

    return _auth

#}}}
def _credsToDict(credentials): #{{{
    '''
    Making a Credentials object into a dictionary
    '''
    return {
        'token' : credentials.token,
        'refresh_token' : credentials.refresh_token,
        'token_uri' : credentials.token_uri,
        'client_id' : credentials.client_id,
        'client_secret' : credentials.client_secret,
        'scopes' : str(credentials.scopes),
    }
#}}}
def _dbToCreds(credsEntry): #{{{

    '''
    Taking a database entry of OAuthCreds, 
    return a Credentials object.
    '''
    #print("checking for oauth creds for ID: ", oauthCredsID)
    #credsEntry = OAuthCreds.query.filter_by(id = oauthCredsID).first()
    credsDict = {
        'token' : credsEntry.token,
        'refresh_token' : credsEntry.refresh_token,
        'token_uri' : credsEntry.token_uri,
        'client_id' : credsEntry.client_id,
        'client_secret' : credsEntry.client_secret,
        'scopes' : list(credsEntry.scopes),
    }

    credentials = google.oauth2.credentials.Credentials(**credsDict)
    return credentials
#}}}
