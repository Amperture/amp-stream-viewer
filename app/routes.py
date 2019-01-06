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

@app.route('/api/searchyt', methods=["POST"]) #{{{
def searchyt():
    '''
    Search youtube live streams.
    '''
    # Process form {{{
    try:
        form        = request.get_json()
        jwt         = request.headers['Authorization']
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
        jwt         = request.headers['Authorization']
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

        except ValueError as ex: 
            errorDetail = str(ex)
            return jsonify({
                'error' : COMMON_ERRORS[errorDetail]
                }), 403
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
        # Required parameters
        videoID     = form['videoID']
        jwt         = request.headers['Authorization']
        # Optional parameters
        '''
        `filtSponsors`  : Whether or not to include paid Members/Sponsors.
        `filtMods`      : Whether or not to include chat Moderators.

        The above 2 variables are optional and have two valid values.
        `only` and `exclude`, if not found, Sponsors/Mods will be included.
        '''
        perPage             = form.get('perPage', 5)
        chatterNameSearch   = form.get('chatterNameSearch', '')
        page                = form.get('page', 0)
        orderBy             = form.get('orderBy', 'numMessages desc')
        filtSponsors        = form.get('filtSponsors', 'include')
        filtMods            = form.get('filtMods', 'include')        
    except Exception as ex:
        print(ex)
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
    # Grab Total Number of Chatters for the Stream {{{

    try:
        numChattersTotal = MessageLog.query\
                .filter_by(stream_id = videoID)\
                .distinct(MessageLog.author_id)\
                .count()
    except Exception as ex:
        print(ex)

    # }}}
    # Grab number of chatters fitting filter criteria {{{

    try:
        numChattersFilter = MessageLog.query\
                .filter_by(stream_id = videoID)

        if filtSponsors == 'exclude':
            numChattersFilter = numChattersFilter.filter_by(is_sponsor = False)
        elif filtSponsors == 'only':
            numChattersFilter = numChattersFilter.filter_by(is_sponsor = True)

        if filtMods == 'exclude':
            numChattersFilter = numChattersFilter.filter_by(is_mod = False)
        elif filtMods == 'only':
            numChattersFilter = numChattersFilter.filter_by(is_mod = True)

        if not chatterNameSearch == '':
            numChattersFilter = numChattersFilter.join(MessageLog.author)\
                    .filter(ChatterLog.author_name.startswith(
                        chatterNameSearch))

        numChattersFilter = numChattersFilter.distinct(MessageLog.author_id)
        numChattersFilterCount = numChattersFilter.count()

    except Exception as ex:
        print(ex)

    # }}}

    try:
        chatActivityRank = _rankChatters(
                videoID, perPage, page, orderBy, filtMods, filtSponsors,
                chatterNameSearch
                )
    except Exception as ex:
        print(ex)
    
    #print(numChattersTotal, numChattersFilterCount)
    response = {
            'jwt'               : jwt,
            'numChatters'       : numChattersTotal,
            'numChattersFilt'   : numChattersFilterCount,
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
        jwt         = request.headers['Authorization']
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
        jwt                 = request.headers['Authorization']
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
    jwt = request.headers['Authorization']
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
@app.route('/api/chatlog', methods=["GET"]) #{{{
def userChatLog():
    # Process form {{{
    try:
        form        = request.args
        print(form)
        # Required parameters
        videoID         = form['videoID']
        logMethod       = form['logMethod']
        jwt             = request.headers['Authorization']
        # Optional parameters
        pageNum         = int(form.get('pageNum', 0))
        resultsPerPage  = int(form.get('resultsPerPage', 10))
        authorID        = form.get('authorID', None)
        msgID           = form.get('msgID', None)
    except Exception as ex:
        print(ex)
        return jsonify({
            'error': "invalid_request"
            }), 500 
    # }}}
    # Test for valid LogMethod. Check that matching key is provided. {{{
    validLogKeys = {
            'msgID'     : { 
                'key'       : msgID,
                'method'    : _chatLogByMsgID
            },
            'authorID'  : { 
                'key'       : authorID,
                'method'    : _chatLogByAuthorID,
            }
    }  
    if validLogKeys[logMethod]['key'] == None:
        return jsonify({
            'error': "invalid_request",
            'detail': ("proper key was not provided "
                "with requested logMethod.")
            }), 500 

    # }}}
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
    # Execute Query {{{
    chatLog, chatLogLen = validLogKeys[logMethod]['method'](
            videoID, 
            validLogKeys[logMethod]['key'], 
            resultsPerPage, 
            pageNum
            )
    # }}}
    return jsonify({
        'jwt'       : jwt,
        'chatLog'   : chatLog,
        'chatLogLen': chatLogLen, 
        })

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
                    messageDict['timestamp'], "%Y-%m-%dT%H:%M:%S.%f%z"), 
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
    # Broadcast may be an ended stream, throw error if so {{{
    if 'actualEndTime' in broadcastInfo['liveStreamingDetails']:
        raise ValueError('liveChatEnded')
    # }}} 


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
def _rankChatters(videoID, perPage, page, #{{{
        orderBy, incMods, incMembers, chatterNameSearch) :
    '''
    Run a query and search for the most active chatters in a stream.
    '''
    messageRanks = []

    # First setup of Query {{{
    query = db.session.query(
            db.func.count(MessageLog.author_id),
            ChatterLog.author_name,
            ChatterLog.avatar,
            ChatterLog.author_channel_id,
            )\
        .join(ChatterLog, 
                MessageLog.author_id == ChatterLog.author_channel_id)\
        .filter(MessageLog.stream_id == videoID)\
        .group_by(ChatterLog.author_channel_id)
    # }}}
    # Filter in or out chat Moderators and Members {{{
    if incMods == 'only':
        query = query.filter(MessageLog.is_mod == True)
    elif incMods == 'exclude':
        query = query.filter(MessageLog.is_mod == False)

    if incMembers == 'only':
        query = query.filter(MessageLog.is_sponsor == True)
    elif incMembers == 'exclude':
        query = query.filter(MessageLog.is_sponsor == False)

    if not chatterNameSearch == '':
        query = query.filter(ChatterLog.author_name.startswith(
            chatterNameSearch))

    #print(query)
    
    # }}} 
    # Setting up the Sorting of the Query {{{
    if orderBy == 'numMessages desc':
        query = query.order_by(desc(db.func.count(MessageLog.author_id)))
    elif orderBy == 'numMessages':
        query = query.order_by(db.func.count(MessageLog.author_id))
    elif orderBy == 'name desc':
        query = query.order_by(desc(ChatterLog.author_name))
    elif orderBy == 'name':
        query = query.order_by(ChatterLog.author_name)
    #print(query)

    # }}}
    # Execute Main chatters Query {{{
    query = query.limit(perPage).offset(page * perPage)
    chatters = query.all()
    # }}}
    # Query for list of Mods and Sponsors {{{
    modQuery = db.session.query(MessageLog.author_id)\
            .filter(MessageLog.stream_id == videoID)\
            .filter(MessageLog.is_mod == True)\
            .distinct(MessageLog.author_id)
    modList = [i[0] for i in modQuery.all()]

    sponsorQuery = db.session.query(MessageLog.author_id)\
            .filter(MessageLog.stream_id == videoID)\
            .filter(MessageLog.is_sponsor == True)\
            .distinct(MessageLog.author_id)
    sponsorList = [i[0] for i in sponsorQuery.all()]
    # }}}
    # Prep and return list for client {{{ 
    for result in chatters:
        rankedMessage = {
                'numMessages'   : result[0],
                'name'          : result[1],
                'avatar'        : result[2],
                'authorID'      : result[3],
                'isMod'         : False,
                'isSponsor'     : False
        }

        if result[3] in modList:
            rankedMessage['isMod'] = True

        if result[3] in sponsorList:
            rankedMessage['isSponsor'] = True

        messageRanks.append(rankedMessage)
    return messageRanks
    # }}}


#}}}
def _chatLogByMsgID(videoID, msgID, perPage, pageNum): #{{{
    '''
    Grab the context of a msgID by grabbing the preceeding and proceeding 
    5 messages from the database.
    '''
    chatLog = []

    # Grab the message in question {{{
    msgFromID = MessageLog.query.filter_by(msg_id = msgID).first()
    # }}}
    # Grab the previous messages {{{
    prevMsgQuery = MessageLog.query.filter_by(stream_id = videoID)\
            .filter(MessageLog.timestamp < msgFromID.timestamp)\
            .order_by(desc(MessageLog.timestamp))

    prevMsgResult = prevMsgQuery.limit(5).all()
    for r in reversed(prevMsgResult): # query will come in reversed order
        chatLog.append({
            'msgID'         : r.msg_id,
            'text'          : r.text,
            'author_name'   : r.author.author_name,
            'avatar'        : r.author.avatar,
            'isMod'         : r.is_mod,
            'isSponsor'     : r.is_sponsor,
            'timestamp'     : r.timestamp,
            })
    # }}}
    # Grab the next messages {{{

    nextMsgQuery = MessageLog.query.filter_by(stream_id = videoID)\
            .filter(MessageLog.timestamp >= msgFromID.timestamp)\
            .order_by(MessageLog.timestamp)

    nextMsgResult = nextMsgQuery.limit(4).all()
    for r in nextMsgResult:
        chatLog.append({
            'msgID'         : r.msg_id,
            'text'          : r.text,
            'author_name'   : r.author.author_name,
            'avatar'        : r.author.avatar,
            'isMod'         : r.is_mod,
            'isSponsor'     : r.is_sponsor,
            'timestamp'     : r.timestamp,
            })

    # }}}
    
    return chatLog, len(chatLog)

#}}}
def _chatLogByAuthorID(videoID, authorID, perPage, pageNum): #{{{
    '''
    Grab the chatlog of a given stream for a specific user.
    '''
    # Query Database Entry for User's Chatlog {{{
    #print(videoID, authorID)
    query = MessageLog.query.filter_by(author_id = authorID)\
            .filter_by(stream_id = videoID)

    r = query.limit(perPage).offset(pageNum * perPage).all()

    chatLogLength = query.count()

    chatLog = []
    for result in r:
        userChatMessage = {
                'msgID'         : result.msg_id,
                'text'          : result.text,
                'author_name'   : result.author.author_name,
                'avatar'        : result.author.avatar,
                'isMod'         : result.is_mod,
                'isSponsor'     : result.is_sponsor,
                'timestamp'     : result.timestamp,
                }
        chatLog.append(userChatMessage)

    # }}}
    return chatLog, chatLogLength

#}}}

