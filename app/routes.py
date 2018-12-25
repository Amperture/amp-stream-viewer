#{{{ Python and Flask Imports
from app import app, lm, db
from flask import redirect, url_for, jsonify, request, send_file

#from flask_dance.contrib.google import google
#from flask_dance.consumer import oauth_authorized

from flask_login import login_required, login_user, logout_user, current_user

from app.models import User, OAuthCreds, StreamLog, ChatterLog, MessageLog, \
        Broadcaster

from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.dialects.postgresql import insert 
from sqlalchemy import desc 

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
@app.route('/api/getstreaminfo', methods=["POST"]) #{{{
def getChatID():
    response = {}
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
    # {{{ Check database for stream info

    stream = StreamLog.query.filter_by(video_id = videoID).first()
    if not stream: 
        # {{{ Make API call and grab Chat ID
        youtube = build('youtube', 'v3', credentials=credentials)
        broadcast = youtube.videos().list(
                part='id,liveStreamingDetails,snippet',
                id=videoID
        ).execute()
        #pprint.pprint(broadcast['items'][0]['snippet'])
        broadcastInfo = broadcast['items'][0]
        stream, broadcaster = _processBroadcastInfo(broadcastInfo)
        # }}}
    broadcaster = stream.streamer

    chatID =  stream.chat_id
    streamerName = broadcaster.channel_name
    streamTitle = stream.video_title
    streamDescription = stream.video_description

    # }}}

    response = {
            'chatID'            : chatID,
            'streamerName'      : streamerName,
            'streamTitle'       : streamTitle,
            'streamDescription' : streamDescription,
            'jwt'               : jwt,
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
    try:
        chatMessages = youtube.liveChatMessages().list(
                part='id,snippet,authorDetails',
                pageToken=chatNextPageToken,
                liveChatId=chatID
        ).execute()
    except Exception as ex:
        print(ex)
        return jsonify({
            'error':'http_error'
            }), 500
    #pprint.pprint(chatMessages)

    messageList = _processChatMessagesForClient(chatMessages, chatID)
    # }}}

    response = {
            'messageList'           : messageList,
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
    '''
    print("User ID: ", u.id)
    print("Creds ID: ", c.id)
    print("User Reference Token: ", u.oauth_creds.token)
    print("Creds Reference Email: ", c.user.email)
    '''


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
def _processChatMessagesForClient(messagesAPIResponse, chatID):#{{{
    '''
    Process the `items` returned by YouTube's liveChatMessageListResponse call
    and return a list of json/dict objects cleaner for the web client.
    '''
    messageList = []
    #pprint.pprint(messagesAPIResponse)
    stream = StreamLog.query.filter_by(chat_id = chatID).first()

    messages = messagesAPIResponse['items']
    for item in messages:
        # Construct JSON Object/Dictionary of message to return to browser {{{
        messageDict = { 
                'msgID'             : item['id'],
                'authorChannelID'   : item['authorDetails']['channelId'],
                'authorName'        : item['authorDetails']['displayName'],
                'isMod'             : item['authorDetails']['isChatModerator'],
                'isOwner'           : item['authorDetails']['isChatOwner'],
                'isSponsor'         : item['authorDetails']['isChatSponsor'],
                'avatar'            : item['authorDetails']['profileImageUrl'],
                'text'              : item['snippet']['displayMessage'],
                'timestamp'         : item['snippet']['publishedAt']
                }
        print(messageDict['authorName'], messageDict['text'])
        messageList.append(messageDict)
        # }}}
        # Upsert the author to the database {{{
        authorInsertStatement = insert(ChatterLog).values(
                author_channel_id = messageDict['authorChannelID'],
                author_name = messageDict['authorName'],
                avatar = messageDict['avatar']
        ).on_conflict_do_update(
                index_elements=['author_channel_id'],
                set_= {
                    'author_name' : messageDict['authorName'],
                    'avatar' : messageDict['avatar']
                    })
        db.session.execute(authorInsertStatement) 
        # }}}
        # No-conflict-Insert the Message to the database {{{
        msgInsertStatement = insert(MessageLog).values(
                author_id = messageDict['authorChannelID'],
                stream_id = stream.video_id,
                msg_id = messageDict['msgID'],
                text = messageDict['text'], 
                timestamp = datetime.datetime.strptime(
                    messageDict['timestamp'], "%Y-%m-%dT%H:%M:%S.%fZ"), 
                isMod = messageDict['isMod'],
                isOwner = messageDict['isOwner'],
                isSponsor = messageDict['isSponsor']
        ).on_conflict_do_nothing(
                index_elements=['msg_id'])
        db.session.execute(msgInsertStatement) 
        # }}}

    if len(messageList) > 0:
        db.session.commit()
    return messageList

#}}}
def _processBroadcastInfo(broadcastInfo):#{{{
    '''
    Take in the broadcast information returned from YouTube, check if logs
    exist in database of broadcast, broadcaster, and update database tables
    if necessary.
    '''
    #pprint.pprint(broadcastInfo)
    # Retrieve broadcaster info from database. Create if vacant. {{{

    '''
    Theoretically these two DB operations could be more efficient as upserts.
    This is worth looking into.
    '''
    broadcaster = Broadcaster.query.filter_by(
            channel_id = broadcastInfo['snippet']['channelId']).first()
    if not broadcaster:
        broadcaster = Broadcaster(
                channel_id = broadcastInfo['snippet']['channelId'],
                channel_name = broadcastInfo['snippet']['channelTitle']
        )
        db.session.add(broadcaster)
    # }}}
    # Retrieve stream info from database. Create if vacant. # {{{
    stream = StreamLog.query.filter_by(
            video_id = broadcastInfo['id']).first()
    if not stream:
        stream = StreamLog(
                video_id = broadcastInfo['id'],
                video_title = broadcastInfo['snippet']['title'],
                video_description = broadcastInfo['snippet']['description'],
                chat_id = 
                    broadcastInfo['liveStreamingDetails']['activeLiveChatId']
        )
        db.session.add(stream)
        broadcaster.streams.append(stream)
    #}}}
    db.session.commit()
    return stream, broadcaster

#}}}
