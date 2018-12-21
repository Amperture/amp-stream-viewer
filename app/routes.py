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

import datetime
import pprint
import json
import os

#}}}

@app.route('/api/searchyt', methods=["POST"]) #{{{
def searchyt():
    '''
    Search youtube live streams.
    '''
    # Process form {{{
    try:
        form        = request.get_json()
        jwt         = form['jwt']
        search_text = form['searchText']
        sort_method = form['sortMethod']
        #print("JWT TOKEN: ", jwt)
        #print("SEARCH TERM: ", search_text)
    except:
        return jsonify({
            'error': "empty_request"
            }), 500 # }}}
    #{{{ Verify Identity and Grab Credentials For API Call
    try:
        user, idInfo = _verifyJWTToken(jwt)
        credentials = _dbToCreds(user.oauth_creds.id)
        #print(credentials)
        #print(user.email)
    except:
        return jsonify({
            'error' : 'invalid_token'
            }), 500

    jwt = _refreshIdTokenIfNeeded(jwt, idInfo, credentials)

    #}}}
    #{{{ Create Youtube stream search API and execute
    youtube = build('youtube', 'v3', credentials=credentials)
    searchResponse = youtube.search().list(
            part='id,snippet',
            q=search_text,
            type='video',
            order=sort_method,
            eventType='live'
    ).execute()
    pprint.pprint(searchResponse)
    #}}}

    response = {
            'searchResult'     :   searchResponse,
            'jwt'              :   jwt
            }

    return jsonify(response)

#}}} 
@app.route('/api/getchatid', methods=["POST"]) #{{{
def getChatID():
    # Process form {{{
    try:
        form        = request.get_json()
        jwt         = form['jwt']
        videoID     = form['videoID']
    except:
        return jsonify({
            'error': "empty_request"
            }), 500 # }}}
    #{{{ Verify Identity and Grab Credentials For API Call
    try:
        user, idInfo = _verifyJWTToken(jwt)
        credentials = _dbToCreds(user.oauth_creds.id)
        #print(credentials)
        #print(user.email)
    except:
        return jsonify({
            'error' : 'invalid_token'
            }), 500

    jwt = _refreshIdTokenIfNeeded(jwt, idInfo, credentials)

    #}}}
    # {{{ Make API call and grab Chat ID
    youtube = build('youtube', 'v3', credentials=credentials)
    broadcast = youtube.videos().list(
            part='id,liveStreamingDetails',
            id=videoID
    ).execute()
    pprint.pprint(broadcast)
    chatID = broadcast['items'][0]['liveStreamingDetails']['activeLiveChatId']
    # }}}

    response = {
            'chatID'        :   chatID,
            'jwt'           :   jwt
            }

    return jsonify(response)

#}}} 
@app.route('/api/getchatmsgs', methods=["POST"]) #{{{
def getChatMsgs():
    # Process form {{{
    try:
        form                = request.get_json()
        jwt                 = form['jwt']
        chatID              = form['chatID']
        chatNextPageToken   = ''
        if 'chatNextPageToken' in form:
            chatNextPageToken = form['chatNextPageToken']
    except:
        return jsonify({
            'error': "empty_request"
            }), 500 

    #}}}
    #{{{ Verify Identity and Grab Credentials For API Call
    try:
        user, idInfo = _verifyJWTToken(jwt)
        credentials = _dbToCreds(user.oauth_creds.id)
        #print(credentials)
        #print(user.email)
    except:
        return jsonify({
            'error' : 'invalid_token'
            }), 500

    jwt = _refreshIdTokenIfNeeded(jwt, idInfo, credentials)

    #}}}
    # {{{ Make API Call to grab chat messages
    youtube = build('youtube', 'v3', credentials=credentials)
    chatMessages = youtube.liveChatMessages().list(
            part='id,snippet,authorDetails',
            pageToken=chatNextPageToken,
            liveChatId=chatID
    ).execute()
    #pprint.pprint(chatMessages)

    messageList = _processChatMessagesForClient(chatMessages['items'])
    # }}}

    response = {
            'messageList'            : messageList,
            'nextPageToken'         : chatMessages['nextPageToken'],
            'pollingIntervalMillis' : chatMessages['pollingIntervalMillis'],
            'jwt'                   : jwt
            }

    #pprint.pprint(response)
    return jsonify(response)

#}}} 
@app.route('/api/sendchatmsg', methods=["POST"]) #{{{
def sendChatMSG():
    # Process form {{{
    try:
        form        = request.get_json()
        jwt         = form['jwt']
        chatID      = form['chatID']
        messageText = form['messageText']
    except:
        return jsonify({
            'error': "empty_request"
            }), 500 

    #}}}
    #{{{ Verify Identity and Grab Credentials For API Call
    try:
        user, idInfo = _verifyJWTToken(jwt)
        credentials = _dbToCreds(user.oauth_creds.id)
        #print(credentials)
        #print(user.email)
    except:
        return jsonify({
            'error' : 'invalid_token'
            }), 500

    jwt = _refreshIdTokenIfNeeded(jwt, idInfo, credentials)

    #}}}
    # {{{ Make API to send Chat Message
    youtube = build('youtube', 'v3', credentials=credentials)
    messageSent = youtube.liveChatMessages().insert(
            part='snippet',
            body={
                'snippet' : {
                    'liveChatId'            : chatID,
                    'type'                  : 'textMessageEvent',
                    'textMessageDetails'    : { 'messageText' : messageText }
                    }
                }
    ).execute()
    pprint.pprint(messageSent)

    # }}}

    response = {
            'sucess'    : True,
            'jwt'       : jwt
            }

    #pprint.pprint(response)
    return jsonify(response)

#}}} 
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
@app.route('/api/userinfo', methods=["POST"]) #{{{
def userInfo(): 
    '''
    Grab User Info from DB, requires JWT token as POST parameter.
    '''
    data = request.get_json()
    jwt = data['jwt']
    try:
        user, idInfo = _verifyJWTToken(jwt)
        sendback = {
            'name' : user.name,
            'email' : user.email, 
            'avatar' : user.avatar,
            'loggedIn' : True
        }
        print(sendback)
        return jsonify(sendback)
    except:
        return jsonify({
            'error' : 'invalid_token'
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
def _dbToCreds(oauthCredsID): #{{{
    '''
    Taking a database entry of OAuthCreds, 
    return a Credentials object.
    '''
    #print("checking for oauth creds for ID: ", oauthCredsID)
    credsEntry = OAuthCreds.query.filter_by(id = oauthCredsID).first()
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
    print("User ID: ", u.id)
    print("Creds ID: ", c.id)
    print("User Reference Token: ", u.oauth_creds.token)
    print("Creds Reference Email: ", c.user.email)


    return u
#}}}
def _refreshIdTokenIfNeeded(jwt, idInfo, credentials):#{{{
    '''
    Compare the expiration timestamp of the jwt token,
    if the token expires in less than fifteen minutes, renew it.
    '''
    now = datetime.datetime.now()
    exp = datetime.datetime.fromtimestamp(idInfo['exp'])
    delta = exp - now
    if(delta >= datetime.timedelta(minutes=15)):
        '''
        print("ACCESS TOKEN: ", credentials.token) 
        print("ID_TOKEN: ", credentials.id_token) 
        print("JWT: ", jwt) 
        '''
        credentials.refresh(requests.Request())
        return credentials.id_token
        '''
        print("ACCESS TOKEN: ", credentials.token) 
        print("ID_TOKEN: ", credentials.id_token) 
        print("JWT: ", jwt) 
        '''

    return jwt
#}}}
def _verifyJWTToken(jwt):#{{{
    '''
    Take a provided JWT token, verify that it is genuine with Google.
    Then verify that it corresponds to an existing user in the database.
    Return that user information from a database call.
    '''
    try:
        idInfo = id_token.verify_oauth2_token(
                jwt, 
                requests.Request(), 
                app.config['GOOGLE_OAUTH_CLIENT_ID']
        )
        #pprint.pprint(idInfo)

        if idInfo['iss'] not in ['accounts.google.com', 
                'https://accounts.google.com']:
            raise ValueError("wrong_issuer")
        
    except Exception as ex:
        print("Error retrieving profile: ", ex)
        pass

    try:
        dbQuery = User.query.filter_by(jwt_sub = idInfo['sub'])
        user = dbQuery.one()
    except Exception as ex:
        print("User Not Found")
        pass

    return user, idInfo
#}}}
def _processChatMessagesForClient(messages):#{{{
    '''
    Process the `items` returned by YouTube's liveChatMessageListResponse call
    and return a list of json/dict objects cleaner for the web client.
    '''
    messageList = []
    for item in messages:
        pprint.pprint(item)
        messageDict = {
                'msgID'             : item['id'],
                'authorChannelID'   : item['authorDetails']['channelId'],
                'authorName'        : item['authorDetails']['displayName'],
                'isMod'             : item['authorDetails']['isChatModerator'],
                'isOwner'           : item['authorDetails']['isChatOwner'],
                'isSponsor'         : item['authorDetails']['isChatSponsor'],
                'avatar'            : item['authorDetails']['profileImageUrl'],
                'text'              : item['snippet']['displayMessage']
                }
        messageList.append(messageDict)
        
    return messageList

#}}}
