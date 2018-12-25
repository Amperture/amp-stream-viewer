<template>  <!--{{{-->
<div>
  <AppHeader/>
  <div class='columns'>
    <!-- Video Container and Info {{{ -->
    <div class='column'>
      <div class='video-container'>
        <iframe 
          width="100%" 
          :height="this.videoPlayerHeight" 
          :src="this.youtubeEmbedURL" 
          frameborder="0" 
          allow="autoplay; encrypted-media" 
          allowfullscreen></iframe>
      </div>
      <div>
        <h1>{{ streamTitle }}</h1>
      </div>
    </div> <!-- }}} -->
    <!-- Chat Table {{{ -->
    <div v-if='chatEnabled == true' class='column is-3'>
      <table ref='chatBox' class='table chat-box'>
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
    <!-- Chat Disabled {{{ -->
    <div v-else class='column is-3'>
      <p>{{ chatEnabledReason }}</p>
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
      streamTitle         : 'check',
      liveChatID          : '',
      chatPolling         : null,
      chatNextPageToken   : null,
      chatNextInterval    : null,
      chatTable           : [],
      chatPollingActive   : true, // flag for chat polling
      chatEnabled         : false,
      chatEnabledReason   : "Hang on a hot second, I'm loading up the chat...",
      messageTextToSend   : null
    }

  }, // }}}
  computed: { // {{{

    youtubeEmbedURL : function() { // {{{
      return 'https://www.youtube.com/embed/' + this.streamID + "?autoplay=1"
    }, // }}}
    videoPlayerHeight : function() { // {{{
      if(this.documentFullWidth < 768) {
        // If we're in mobile mode, video player will stack vertically with
        // chat. Just make the 16:9 conversion.
        return (this.documentFullWidth * (9/16))
      } else {
        // ...but if we're in Desktop mode, the chat will take up 1/4th of 
        // the window, so we need to also account for those pixels as well.
        return (this.documentFullWidth * (3/4) * (9/16))
      }
    } // }}}

  }, // }}}
  methods: { // {{{ 

    addChatMessagesToTable(messageList){// {{{
      this.chatTable = this.chatTable.concat(messageList)
      if(this.chatTable.length > 50){
        this.chatTable = this.chatTable.slice(-50)
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
          this.addChatMessagesToTable(response.messageList)
          this.chatEnabled = true
          this.$nextTick(() => {
            this.$refs.chatBox.scrollTop = this.$refs.chatBox.scrollHeight
          })
          this.chatNextInterval = response.pollingIntervalMillis
          this.chatNextPageToken = response.nextPageToken

          if (this.chatPollingActive == true){
            this.chatPolling = setTimeout(() => {
              this.pollChatMessages()
            }, this.chatNextInterval)
          }
        })
        .catch((error) => { // {{{ 
          console.log(error)
          switch(error){
            case 'http_error': // {{{

              // If this is a simple http error, then it was likely just a 
              // youtube problem, wait 5 seconds and try again.
              this.chatPolling = setTimeout(() => {
                this.pollChatMessages()
              }, 5000)
              break

            // }}}
          } 
        }) // }}}

    }, // }}}
    handleSendChat(){ // {{{
      this.$store.dispatch(
        'sendLiveChatMessage', {
          chatID      : this.liveChatID,
          messageText : this.messageTextToSend
        })
        .then((response) => {
          this.messageTextToSend = null
        })
    }, // }}}
    handleResize(){ // {{{
      this.documentFullWidth = document.documentElement.clientWidth
    } // }}}

  }, // }}}
  beforeDestroy(){ // {{{
    this.chatActive = false // Disable chat polling.
    // clearTimeout(this.chatPolling)
    window.removeEventListener('resize', this.handleResize)
  }, // }}}
  mounted(){ // {{{
    // Handling Window Resizing
    window.addEventListener('resize', this.handleResize)

    // Make sure chat is scrolled to bottom of box at spawn.
    this.$refs.chatBox.scrollTop = this.$refs.chatBox.scrollHeight
  }, // }}}
  created(){ // {{{
    this.$store.dispatch('grabVideoChatID', this.streamID)
      .then((response) => {
        //console.log(response)
        this.liveChatID = response.chatID
        //console.log("FRESH RETEIVE CHAT ID: ", this.liveChatID)
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
