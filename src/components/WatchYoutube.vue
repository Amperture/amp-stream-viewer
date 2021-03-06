<template>  <!--{{{-->
<div>
  <AppHeader/>
  <section class='section'>
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
            <h1 class='title is-5'>{{ streamTitle }}</h1>
            <h1 class='subtitle is-6'>by {{ streamerName }}</h1>
            <router-link
              :to="{ name : 'YoutubeStreamStats', query : { watch : this.streamID } }">
              View Stream/Chat Stats</router-link>
          </div>
        </div> <!-- }}} -->
        <!-- Chat Table {{{ -->
        <div v-if='chatEnabled == true' class='column is-3'>
          <table class='table chat-table'>
            <tbody class='chat-table-body' ref='chatBox'>
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
              <div v-bind:class="chatInputControlClass">
                <input 
                  v-bind:class="chatInputBoxClass" 
                  v-model='messageTextToSend' 
                  :disabled='chatInputBoxClass.disabled'
                  type="text" 
                  placeholder="Chat!">
              </div>
            </div>
          </form><!--}}}-->
        </div> <!--}}}-->
        <!-- Chat Disabled {{{ -->
        <div v-else class='column is-3'>
          <p>{{ reasons[chatEnabledReason] }}</p>
        </div> <!--}}}-->
      </div>
  </section>
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
      documentFullWidth     : document.documentElement.clientWidth,
      streamID              : this.$route.query.watch,
      streamTitle           : '',
      streamDescription     : '',
      streamerName          : '',
      liveChatID            : '',
      messageTextToSend     : null,
      messageSentSuccess    : null,
      messageSentFail       : null,
      chatPolling           : null,
      chatNextPageToken     : null,
      chatNextInterval      : null,
      chatTable             : [],
      chatPollingActive     : true, // flag for chat polling
      chatEnabled           : false,
      chatEnabledReason     : 'loading',
      reasons               : {
         'loading'        : "Hang on a hot second, I'm loading the chat...",
         'chat_disabled'  : "This streamer went and disabled chat, that's too bad!",
         'chat_not_found' : "I don't think this is a live video, I can't find chat!",
         'chat_ended'     : "Alright, fun's over. Chat's ended. We're done here!",
      },
      chatInputBoxClass   : {
        'input'       : true,
        'disabled'    : false,
        'is-danger'   : false,
        'is-success'  : false,
      },
      chatInputControlClass : {
        'control'     : true,
        'is-loading'  : false
      }, 

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
      this.$store.dispatch('grabLiveChatMessages', {
        chatID              : this.liveChatID,
        videoID             : this.streamID,
        chatNextPageToken   : this.chatNextPageToken
      })
        .then((response) => { // {{{
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
        }) // }}}
        .catch((error) => { // {{{ 
          console.log(error.status)
          console.log(error.response.data)
          switch(error.response.data.error){
            case 'yt_backend_error': // {{{

              // If this is a simple http error, then it was likely just a 
              // youtube problem, wait 5 seconds and try again.
              this.chatPolling = setTimeout(() => {
                this.pollChatMessages()
              }, 5000)
              break

            // }}}
            case 'invalid_token': // {{{

              // User was logged out or sent an invalid token somehow.
              // Send them back to Login Component.
              this.$router.push('login') 
              break

            // }}}
            case 'chat_ended': // {{{

              // Looks like the chat is over.
              this.chatEnabledReason = 'chat_ended'
              break

            // }}}
            case 'chat_disabled': // {{{

              this.chatEnabledReason = 'chat_disabled'
              break

            // }}}
            case 'chat_not_found': // {{{

              this.chatEnabledReason = 'chat_not_found'
              break

            // }}}
          } 
        }) // }}}

    }, // }}}
    handleSendChat(){ // {{{
      this.chatInputBoxClass.disabled = true
      this.chatInputControlClass['is-loading'] = true
      this.$store.dispatch(
        'sendLiveChatMessage', {
          chatID      : this.liveChatID,
          messageText : this.messageTextToSend
        })
        .then((response) => {
          this.chatInputBoxClass.disabled = false
          this.chatInputControlClass['is-loading'] = false
          this.messageTextToSend = null
          this.chatInputBoxClass['is-success'] = true
          setTimeout(() => { 
            console.log("no more sucess class!")
            this.chatInputBoxClass['is-success'] = false;
          }, 5000)
        })
        .catch((error) => {
          this.chatInputControlClass['is-loading'] = false
          this.chatInputBoxClass.disabled = false
          this.messageTextToSend = null
          this.chatInputBoxClass['is-danger'] = true
          this.messageSentFail = setTimeout(() => { 
            console.log("no more failures!")
            this.chatInputBoxClass['is-danger'] = false;
          }, 5000)
        })
    }, // }}}
    handleResize(){ // {{{
      this.documentFullWidth = document.documentElement.clientWidth
    } // }}}

  }, // }}}
  beforeDestroy(){ // {{{
    // Disable chat polling.
    this.chatPollingActive = false
    clearTimeout(this.chatPolling)

    window.removeEventListener('resize', this.handleResize)
  }, // }}}
  mounted(){ // {{{
    // Handling Window Resizing
    window.addEventListener('resize', this.handleResize)

  }, // }}}
  created(){ // {{{
    this.$store.dispatch('grabStreamInfo', this.streamID)
      .then((response) => {
        //console.log(response)
        this.liveChatID = response.chatID
        this.streamTitle = response.streamTitle 
        this.streamerName = response.streamerName 
        this.streamDescription = response.streamDescription 
        //console.log("FRESH RETEIVE CHAT ID: ", this.liveChatID)
        this.pollChatMessages()
      })
      .catch((error) => { // {{{ 

        console.log(error.status)
        console.log(error.response.data)
        switch(error.response.data.error){
          case 'yt_backend_error': // {{{

            // If this is a simple http error, then it was likely just a 
            // youtube problem, wait 5 seconds and try again.
            this.chatPolling = setTimeout(() => {
              this.pollChatMessages()
            }, 5000)
            break

          // }}}
          case 'invalid_token': // {{{

            // User was logged out or sent an invalid token somehow.
            // Send them back to Login Component.
            this.$router.push('login') 
            break

          // }}}
          case 'chat_ended': // {{{

            // Looks like the chat is over.
            this.chatEnabledReason = 'chat_ended'
            break

          // }}}
          case 'chat_disabled': // {{{

            this.chatEnabledReason = 'chat_disabled'
            break

          // }}}
          case 'chat_not_found': // {{{

            this.chatEnabledReason = 'chat_not_found'
            break

          // }}}
        } 

      }) // }}}

  } // }}}
}

</script> /* }}} */
<style> /* {{{ */
.chat-table {
  width: 100%;
}

.chat-table-body {
  display: block; 
  min-height: 360px;
  max-height: 720px;
  width: 100%;
  overflow-y: auto;
  overflow-x: auto;
  position: relative;
  bottom: 0;
}

.chat-box{
  font-family: Roboto, Arial, sans-serif;
  font-size: 13px;
}

.subtitle{
  color: hsl(0, 0%, 71%);
}
.is-danger{
  border-width: 3px;
}
.is-success{
  border-width: 3px;
}
</style> /* }}} */
