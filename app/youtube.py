# Python and Flask Imports {{{
from app import app, db
from flask import redirect, jsonify, request

from app.util import auth_required

from app.models import User, OAuthCreds, StreamLog, ChatterLog, MessageLog, \
        Broadcaster, chatters_in_stream

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

import json
# }}} 

COMMON_ERRORS = { # {{{
        'backendError'      : "yt_backend_error",
        'liveChatEnded'     : 'chat_ended',
        'liveChatNotFound'  : 'chat_not_found',
        'liveChatDisabled'  : 'chat_disabled',
        }
# }}}

@app.route('/api/youtube/search', methods=["GET"]) #{{{
@auth_required
def youtube_search_get(user):
    '''
    Search youtube live streams.
    '''
    # Process form {{{

    try:
        form        = request.args
        # Required Arguemnts
        sortMethod = form['sortMethod']
        # Optional Arguments
        searchText = form.get('searchText')
        searchMethod = form.get('searchMethod', '')
    except:
        return jsonify({
            'error': "empty_request"
            }), 500 

    # }}}
    # Sometimes a user will just want to repeat their last search {{{
    if (searchMethod == 'lastSearch'):
        searchText = user['user'].last_search
    # }}}
    # {{{ Create Youtube stream search API and execute

    try:
        youtube = build('youtube', 'v3', credentials=user['credentials'])
        searchResult = youtube.search().list(
                part='id,snippet',
                q=searchText,
                type='video',
                maxResults=10,
                relevanceLanguage='en',
                order=sortMethod,
                eventType='live'
        ).execute()
        user['user'].last_search = searchText
        db.session.commit()
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
    #}}}

    response = {
            'searchResult'     :   searchResult,
            'jwt'              :   user['jwt']
            }

    return jsonify(response)

#}}} 
@app.route('/api/youtube/stream', methods=["GET"]) #{{{
@auth_required
def youtube_stream_get(user):
    response = {}
    # Process form {{{
    try:
        videoID = request.args['videoID']
    except KeyError:
        return jsonify({
            'error': "empty_request"
            }), 500 
    # }}}
    # {{{ Check database for stream info, pull from YT API if not found.

    stream = StreamLog.query.filter_by(video_id = videoID).first()
    if not stream: 
        # {{{ Make API call and grab Chat ID
        try:
            youtube = build('youtube', 'v3', credentials=user['credentials'])
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
            'jwt'               : user['jwt']
            }

    return jsonify(response)

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
