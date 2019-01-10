# Potential Features List

This is not meant to be taken as a true `TODO` of expected features.  
Some are going to be more mission critical at later timeframes than others.  
Most of these are nice ideas that would be neat to implement.  
Maybe think of it as a non-timestamped dev-diary.  

## Youtube Info/API
- [ ] Use and Display Concurrent Viewer Data
  * [Videos Endpoint](https://developers.google.com/youtube/v3/docs/videos#liveStreamingDetails): `liveStreamingDetails.concurrentViewers`
  * Perhaps a `snapshot` table? 1- or 30-minute intervals.
  * [D3](https://d3js.org/) to make nice graphs for stats
- [ ] Relative Timestamps for Streams 
  * [Videos Endpoint](https://developers.google.com/youtube/v3/docs/videos#liveStreamingDetails): `liveStreamingDetails.actualStartTime` object
  * All current timestamps shown in GMT, would be nice to see timestamps shown in time since stream went live.
- [ ] Timezone-aware Timestamps for Streams 
  * [Videos Endpoint](https://developers.google.com/youtube/v3/docs/videos#liveStreamingDetails): `liveStreamingDetails.actualStartTime` object
  * Getting Timezone data from viewers is the hard part because there are several options.
    * Educated guess from IP Geolocation?
    * `settings` page per-user?
    * Dropdown on `ytstats` page? 
- [ ] Better/More Error handling
  * [Youtube Data API Errors](https://developers.google.com/youtube/v3/docs/errors)
  * [Youtube Live API Errors](https://developers.google.com/youtube/v3/live/docs/errors)
  * Will need to parse through these and see which ones are most relevant to our app.

## Chat API
- [ ] Better segregation of `liveChatMessages` types.
  * [LiveChatMessages endpoint](https://developers.google.com/youtube/v3/live/docs/liveChatMessages#snippet.type) `snippet.type` object
  * System currently simply displays all text as messages.
  * `superChatEvent` could be tracked for stats w.r.t. money raised.
    * [`superChatDetails`](https://developers.google.com/youtube/v3/live/docs/liveChatMessages#snippet.superChatDetails) for storing amount.
  * `tombstone` and `userBannedEvent`  would be good data to use for moderator logs.
    * Would need to create mod- and owner-only stats pages.
- [ ] Rolling timeframes for chatlog.
  * Example Query Filter:
    
```python
MessageLog.query\
  .filter_by(stream_id = videoID)\
  .filter_by(timestamp > (datetime.utcnow() - datetime.timedelta(minutes = 5))
```

## Stream Viewing Page
- [ ] Better implementation of non-text event types.
  * See Chat API section above.
- [ ] Better display 
- [ ] Error handling to include user chat rights.
  * Disable chat input box if user not allowed to chat.
    * Banned
    * Non-Sponsor during Sponsor-Only Chat
- [ ] Error handling to include streamer settings.
  * Disabled Embedding
  * Disabled Chat

## Stream Searching
- [ ] Locale Support
  * Currently hard codes searches to `relevanceLanguage = 'en'`
  * Also has several options for setting up.
