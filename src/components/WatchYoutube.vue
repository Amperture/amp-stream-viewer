<template>  <!--{{{-->
<div>
  <AppHeader/>
  <div class='columns'>
    <div class='column video-container'> <!-- Video Container {{{ -->
      <iframe 
        width="100%" 
        :height="this.videoPlayerHeight" 
        :src="this.youtubeEmbedURL" 
        frameborder="0" 
        allow="autoplay; encrypted-media" 
        allowfullscreen></iframe>
    </div> <!-- }}} -->
    <div class='column is-3'> <!-- Chat Table {{{--> 
      <table class='table chat-box'>
        <tbody>
          <tr v-for="message in chatTable">
            <td>
              <figure class='image is-24x24'>
                <img class='is-rounded' v-bind:src="message.avatar"/>
              </figure>
            </td>
            <td><strong>{{ message.authorName }}</strong>
            {{ message.text }}</td>
          </tr>
        </tbody>
      </table>
      <form @submit.prevent='handleSendChat'><!--Send Chat Form {{{-->
        <div class='field'> 
          <div class="control">
            <input class="input" v-model='messageTextToSend' type="text" placeholder="Chat!">
          </div>
        </div>
      </form><!--}}}-->
    </div> <!--}}}-->
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
      documentFullWidth   : document.documentElement.clientWidth,
      streamID            : this.$route.query.watch,
      liveChatID          : null,
      chatPolling         : null,
      chatNextPageToken   : null,
      chatNextInterval    : null,
      chatTable           : [],
      messageTextToSend   : null
    }

  }, // }}}
  computed: { // {{{

    youtubeEmbedURL : function() { // {{{
      return 'https://www.youtube.com/embed/' + this.streamID;
    }, // }}}
    videoPlayerHeight : function() {
      if(this.documentFullWidth < 768) {
        // If we're in mobile mode, video player will stack vertically with
        // chat. Just make the 16:9 conversion.
        return (this.documentFullWidth * (9/16))
      } else {
        // ...but if we're in Desktop mode, the chat will take up 1/4th of 
        // the window, so we need to also account for those pixels as well.
        return (this.documentFullWidth * (3/4) * (9/16))
      }
    }

  }, // }}}
  methods: { // {{{ 

    addChatMessagesToTable(messageList){// {{{
      this.chatTable = this.chatTable.concat(messageList)
      if(this.chatTable.length > 50){
        this.chatTable = this.chatTable.slice(-50);
      }
    }, // }}}
    pollChatMessages(){ // {{{
      // Dispatch Action to Grab Chat Messages
      //console.log("Polling for Chat Messages")
      this.$store.dispatch('getLiveChatMessages', {
        chatID              : this.liveChatID,
        chatNextPageToken   : this.chatNextPageToken
      })
        .then((response) => {
          // Messages Successfully grabbed, start setting up next poll.
          this.addChatMessagesToTable(response.messageList); 

          this.chatNextInterval = response.pollingIntervalMillis;
          this.chatNextPageToken = response.nextPageToken;

          this.chatPolling = setTimeout(() => {
            this.pollChatMessages();
          }, this.chatNextInterval);
        })
        .catch((error) => {

        })

    }, // }}}
    handleSendChat(){ // {{{
      this.$store.dispatch(
        'sendLiveChatMessage', {
          chatID      : this.liveChatID,
          messageText : this.messageTextToSend
        })
        .then((response) => {
          this.messageTextToSend = null;
        })
    }, // }}}
    handleResize(){ // {{{
      this.documentFullWidth = document.documentElement.clientWidth
    } // }}}

  }, // }}}
  beforeDestroy(){ // {{{
    clearTimeout(this.chatPolling)
    window.removeEventListener('resize', this.handleResize)
  }, // }}}
  mounted(){ // {{{
    window.addEventListener('resize', this.handleResize)
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
<style> /* {{{ */
tbody{
  display: block;
  min-height: 360px;
  max-height: 720px;
  overflow-y: auto;
  overflow-x: auto;
  position: relative;
  bottom: 0;
}

.chat-box{
  font-family: Roboto, Arial, sans-serif;
  font-size: 13px;
}
</style> /* }}} */
