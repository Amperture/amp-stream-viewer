<template>  <!--{{{-->
<div>
<AppHeader/>
<div class="video-container">
  <iframe width="640" height="360" :src="this.youtubeEmbedURL" frameborder="0" allow="autoplay; encrypted-media" allowfullscreen></iframe>
</div>
</div>
</template> <!--}}}-->

<script> /* {{{ */

import Header from './Header'

export default {
  components: { // {{{
    'AppHeader' : Header

  }, // }}}
  data() { // {{{ 

    return {
      streamID            : this.$route.query.watch,
      liveChatID          : null,
      chatPolling         : null,
      chatNextPageToken   : null,
      chatNextInterval    : null,
    }

  }, // }}}
  computed: { // {{{

    youtubeEmbedURL : function() {
      return 'https://www.youtube.com/embed/' + this.streamID;
    }

  }, // }}}
  methods: { // {{{ 
    pollChatMessages(){ // {{{
      // Dispatch Action to Grab Chat Messages
      //console.log("Polling for Chat Messages")
      this.$store.dispatch('getLiveChatMessages', {
        chatID              : this.liveChatID,
        chatNextPageToken   : this.chatNextPageToken
      })
        .then((response) => {
          // Messages Successfully grabbed, start setting up next poll.
          this.chatNextInterval = response.pollingIntervalMillis;
          this.chatNextPageToken = response.nextPageToken;
          this.chatPolling = setTimeout(() => {
            this.pollChatMessages();
          }, this.chatNextInterval);
        })
        .catch((error) => {

        })

    } // }}}
  }, // }}}
  beforeDestroy(){ // {{{
    clearTimeout(this.chatPolling)
  }, // }}}
  created(){ // {{{
    this.$store.dispatch('grabVideoChatID', this.streamID)
      .then((response) => {
        //console.log(response);
        this.liveChatID = response.chatID;
        //console.log("FRESH RETEIVE CHAT ID: ", this.liveChatID);
        this.pollChatMessages()
      })
      .catch((error)  =>  {
        console.log("Something went wrong, apparently")

      }) 
  } // }}}
}

</script> /* }}} */

