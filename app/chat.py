# Imports {{{
from app import app, db
from app.models import StreamLog, MessageLog, ChatterLog
from app.util import auth_required, function_timer

from flask import jsonify, request

from sqlalchemy import desc
from sqlalchemy.orm.exc import NoResultFound, FlushError
from sqlalchemy.exc import IntegrityError
from sqlalchemy.dialects.postgresql import insert 

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

import datetime
import json
import pytz
# }}}

COMMON_ERRORS = { # {{{
        'backendError'      : "yt_backend_error",
        'liveChatEnded'     : 'chat_ended',
        'liveChatNotFound'  : 'chat_not_found',
        'liveChatDisabled'  : 'chat_disabled',
        }
# }}}

@app.route('/api/chat/youtube', methods=["POST"]) #{{{
@function_timer
@auth_required
def chat_youtube_post(user):
    # Process form {{{
    try:
        form        = request.get_json()
        chatID      = form['chatID']
        messageText = form['messageText']
    except:
        return jsonify({
            'error': "empty_request"
            }), 500 

    #}}}
    # {{{ Make API to send Chat Message
    try:
        youtube = build('youtube', 'v3', credentials=user['credentials'])
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
            'jwt'       : user['jwt']
            }

    #pprint.pprint(response)
    return jsonify(response)

#}}} 
@app.route('/api/chat/youtube', methods=["GET"]) #{{{
@function_timer
@auth_required
def chat_youtube_get(user):
    # Process form {{{
    try:
        form                = request.args
        # Required Args
        videoID             = form['videoID']
        chatID              = form['chatID']
        # Optional Args
        chatNextPageToken   = form.get('chatNextPageToken', '')

    except KeyError:
        return jsonify({
            'error': "empty_request"
            }), 500 

    #}}}
    # {{{ Make API Call to grab chat messages
    youtube = build('youtube', 'v3', credentials=user['credentials'])
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
            'jwt'                   : user['jwt']
            }

    #pprint.pprint(response)
    return jsonify(response)

#}}} 
@app.route('/api/chat/youtube/stats', methods=["GET"]) #{{{
@auth_required
def chat_youtube_stats_get(user):
    # Process form {{{
    try:
        form        = request.args
        # Required parameters
        videoID     = form['videoID']
        # Optional parameters
        '''
        `filtSponsors`  : Whether or not to include paid Members/Sponsors.
        `filtMods`      : Whether or not to include chat Moderators.

        The above 2 variables are optional and have two valid values.
        `only` and `exclude`, if not found, Sponsors/Mods will be included.
        '''
        resultsPerPage      = int(form.get('perPage', 5))
        pageNum             = int(form.get('page', 0))
        chatterNameSearch   = form.get('chatterNameSearch', '')
        orderBy             = form.get('orderBy', 'numMessages desc')
        filtSponsors        = form.get('filtSponsors', 'include')
        filtMods            = form.get('filtMods', 'include')        
    except Exception as ex:
        print(ex)
        return jsonify({
            'error': "empty_request"
            }), 500 # }}}
    # {{{ Check database for stream stats

    try:
        stream = StreamLog.query.filter_by(video_id = videoID).first()
        if not stream:
            return jsonify({
                'error' : 'stream_info_not_found'
            }), 401
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
        return jsonify({
            'error' : 'unknown_backend_error'
            }), 500

    # }}}

    try:
        chatActivityRank = _rankChatters(
                videoID, resultsPerPage, pageNum, orderBy, filtMods, filtSponsors,
                chatterNameSearch
                )
    except Exception as ex:
        print(ex)
    
    #print(numChattersTotal, numChattersFilterCount)
    response = {
            'jwt'               : user['jwt'],
            'numChatters'       : numChattersTotal,
            'numChattersFilt'   : numChattersFilterCount,
            'streamTitle'       : stream.video_title,
            'streamerName'      : stream.streamer.channel_name,
            'chatActivityRank'  : chatActivityRank
            }

    return jsonify(response)

#}}} 
@app.route('/api/chat/youtube/log', methods=["GET"]) #{{{
@auth_required
def chat_youtube_log_get(user):
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
    # Execute Query {{{
    chatLog, chatLogLen = validLogKeys[logMethod]['method'](
            videoID, 
            validLogKeys[logMethod]['key'], 
            resultsPerPage, 
            pageNum
            )
    # }}}
    return jsonify({
        'jwt'       : user['jwt'],
        'chatLog'   : chatLog,
        'chatLogLen': chatLogLen, 
        })

#}}}

def _rankChatters(videoID, resultsPerPage, pageNum, #{{{
        orderBy, incMods, incMembers, chatterNameSearch) :
    '''
    Run a query for the active chatters in a stream
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

    # }}}
    # Execute Main chatters Query {{{
    query = query.limit(resultsPerPage).offset(pageNum * resultsPerPage)
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

        author_upsert = insert(ChatterLog).values(
                author_channel_id = messageDict['authorChannelID'],
                author_name = messageDict['authorName'],
                avatar = messageDict['avatar']
                ).on_conflict_do_update(
                    set_=dict(
                        author_channel_id = messageDict['authorChannelID'],
                        author_name = messageDict['authorName'],
                        avatar = messageDict['avatar']
                    ),
                    index_elements=['author_channel_id']
                    )


        try:
            #db.session.add(author)
            db.session.execute(author_upsert)
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
