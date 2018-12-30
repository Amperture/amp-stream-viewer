#{{{ Python and Flask Imports
from app import app, lm, db
from flask import redirect, url_for, jsonify, request, send_file

#from flask_dance.contrib.google import google
#from flask_dance.consumer import oauth_authorized

from flask_login import login_required, login_user, logout_user, current_user

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
    try:
        youtube = build('youtube', 'v3', credentials=credentials)
        searchResponse = youtube.search().list(
                part='id,snippet',
                q=search_text,
                type='video',
                relevanceLanguage='en',
                order=sort_method,
                eventType='live'
        ).execute()
    except HttpError as ex:
        contentJSON = json.loads(ex.content)
        errorDetail = contentJSON['error']['errors'][0]['reason']
        if errorDetail in COMMON_ERRORS.keys():
            return jsonify({
                'error' : COMMON_ERRORS[errorDetail]
                }), ex.resp.status
        else:
            print(ex)
            return jsonify({
                'error' : 'unknown_error'
                }), 500
        
    #pprint.pprint(searchResponse)
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
    # {{{ Check database for stream info, pull from YT API if not found.

    stream = StreamLog.query.filter_by(video_id = videoID).first()
    if not stream: 
        # {{{ Make API call and grab Chat ID
        try:
            youtube = build('youtube', 'v3', credentials=credentials)
            broadcast = youtube.videos().list(
                    part='id,liveStreamingDetails,snippet',
                    id=videoID
            ).execute()
            #pprint.pprint(broadcast['items'][0]['snippet'])
            broadcastInfo = broadcast['items'][0]
            stream, broadcaster = _processBroadcastInfo(broadcastInfo)
        except HttpError as ex:
            contentJSON = json.loads(ex.content)
            errorDetail = contentJSON['error']['errors'][0]['reason']
            if errorDetail in COMMON_ERRORS.keys():
                return jsonify({
                    'error' : COMMON_ERRORS[errorDetail]
                    }), ex.resp.status
            else:
                print(ex)
                return jsonify({
                    'error' : 'unknown_error'
                    }), 500
        # }}}
    else:
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
@app.route('/api/getstreamstats', methods=["POST"]) #{{{
def getStreamStats():
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
    # {{{ Check database for stream stats

    try:
        stream = StreamLog.query.filter_by(video_id = videoID).first()
        if not stream:
            return jsonify({
                'error' : 'stream_info_not_found'
            }), 500
    except Exception as ex:
        print(ex)

    # }}}

    try:
        numChatters = ChatterLog.query\
                .join(ChatterLog.stream)\
                .filter_by(video_id = videoID)\
                .count()
    except Exception as ex:
        print(ex)

    try:
        chatActivityRank = _rankChatters(videoID)
    except Exception as ex:
        print(ex)
    
    response = {
            'jwt'               : jwt,
            'numChatters'       : numChatters,
            'streamTitle'       : stream.video_title,
            'streamerName'      : stream.streamer.channel_name,
            'chatActivityRank'  : chatActivityRank
            }

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
    try:
        youtube = build('youtube', 'v3', credentials=credentials)
        messageSent = youtube.liveChatMessages().insert(
                part='snippet',
                body={
                    'snippet' : {
                        'liveChatId'            : chatID,
                        'type'                  : 'textMessageEvent',
                        'textMessageDetails'    : { 
                            'messageText' : messageText 
                            }
                        }
                    }
        ).execute()
        #pprint.pprint(messageSent)
    except HttpError as ex:
        contentJSON = json.loads(ex.content)
        errorDetail = contentJSON['error']['errors'][0]['reason']
        if errorDetail in COMMON_ERRORS.keys():
            return jsonify({
                'error' : COMMON_ERRORS[errorDetail]
                }), ex.resp.status
        else:
            print(ex)
            return jsonify({
                'error' : 'unknown_error'
                }), 500

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
@app.route('/api/getchatmsgs', methods=["POST"]) #{{{
def getChatMsgs():
    # Process form {{{
    try:
        form                = request.get_json()
        jwt                 = form['jwt']
        videoID             = form['videoID']
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
    except HttpError as ex:
        contentJSON = json.loads(ex.content)
        errorDetail = contentJSON['error']['errors'][0]['reason']
        if errorDetail in COMMON_ERRORS.keys():
            return jsonify({
                'error' : COMMON_ERRORS[errorDetail]
                }), ex.resp.status
        else:
            return jsonify({
                'error' : 'unknown_error'
                }), 500
    #pprint.pprint(chatMessages)

    messageList = _processChatMessagesForClient(chatMessages, videoID)
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
        #print(sendback)
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
@app.route('/api/errortest', methods=["GET"]) #{{{
def errortest():
    '''
    Google OAuth Redirect
    '''
    return jsonify({
        'error' : 'test_error'
        }), 500

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
    if(delta <= datetime.timedelta(minutes=15)):
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
def _processChatMessagesForClient(messagesAPIResponse, videoID):#{{{
    '''
    Process the `items` returned by YouTube's liveChatMessageListResponse call
    and return a list of json/dict objects cleaner for the web client.
    '''
    messageList = []
    #pprint.pprint(messagesAPIResponse)
    stream = StreamLog.query.filter_by(video_id = videoID).first()

    messages = messagesAPIResponse['items']
    for item in messages:
        # Construct JSON Object/Dictionary of message to return to browser {{{
        try:
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
        except Exception as ex:
            pprint.pprint(item)
            print(ex)
        #print(messageDict['authorName'], messageDict['text'])
        messageList.append(messageDict)
        # }}}
        # Upsert the author to the database {{{
        author = ChatterLog(
                author_channel_id = messageDict['authorChannelID'],
                author_name = messageDict['authorName'],
                avatar = messageDict['avatar']
                )
        try:
            db.session.add(author)
            db.session.commit()
        except IntegrityError:
            #print("Author already known, skipping.")
            db.session.rollback()
        except FlushError:
            #print("Author already known, skipping.")
            db.session.rollback()
        except Exception as ex:
            #print(ex)
            db.session.rollback()

        # }}}
        # Append author to stream as chatter. {{{

        try:
            stream.chatters.append(author)
            db.session.commit()
        except FlushError or IntegrityError:
            #print("Chatter already recorded in chat session, skipping.")
            db.session.rollback()
        except Exception as ex:
            #print(ex)
            db.session.rollback()

        # }}}
        # Insert the Message to the database {{{
        message = MessageLog(
                stream_id = stream.video_id,
                author_id = author.author_channel_id,
                msg_id = messageDict['msgID'],
                text = messageDict['text'], 
                timestamp = datetime.datetime.strptime(
                    messageDict['timestamp'], "%Y-%m-%dT%H:%M:%S.%fZ"), 
                is_mod = messageDict['isMod'],
                is_owner = messageDict['isOwner'],
                is_sponsor = messageDict['isSponsor']
                )
        try:
            db.session.add(message)
            db.session.commit()
        except IntegrityError or FlushError as ex:
            #print(ex)
            #print("Chatlog already found, skipping")
            db.session.rollback()
        except Exception as ex:
            print(ex)
            db.session.rollback()
        # }}}

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
        try: 
            db.session.add(broadcaster)
            db.session.commit()
        except Exception as ex:
            print(ex)
            db.session.rollback()
    # }}}
    # Retrieve stream info from database. Create if vacant. # {{{
    stream = StreamLog.query.filter_by(
            video_id = broadcastInfo['id']).first()
    if not stream:
        stream = StreamLog(
                video_id = broadcastInfo['id'],
                video_title = broadcastInfo['snippet']['title'],
                video_description = broadcastInfo['snippet']['description'],
                streamer_id = broadcaster.channel_id,
                chat_id = 
                    broadcastInfo['liveStreamingDetails']['activeLiveChatId']
        )
        try: 
            db.session.add(stream)
            db.session.commit()
        except Exception as ex:
            print(ex)
            db.session.rollback()
    #}}}
    return stream, broadcaster

#}}}
def _rankChatters(videoID):#{{{
    '''
    Run a query and search for the most active chatters in a stream.
    '''
    messageRanks = []

    r = db.session.query(
            db.func.count(MessageLog.author_id),
            ChatterLog.author_name,
            ChatterLog.avatar
            )\
        .join(ChatterLog, 
                MessageLog.author_id == ChatterLog.author_channel_id)\
        .filter(MessageLog.stream_id == videoID)\
        .group_by(ChatterLog.author_channel_id)\
        .order_by(desc(db.func.count(MessageLog.author_id)))\
        .limit(5).all() 

    for result in r:
        rankedMessage = {
                'numMessages'   : result[0],
                'name'          : result[1],
                'avatar'        : result[2] 
        }
        messageRanks.append(rankedMessage)
    return messageRanks


#}}}

