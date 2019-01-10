<template> <!--{{{-->
<div>  
<AppHeader/>
  <section class="hero">
    <div class="hero-body">
      <div class="container has-text-centered">
        <h2 class="title">Search For YouTube Live Streams</h2>
        <h3 class="subtitle">Please use the search bar above to find a stream you would like to watch!</h3>
        <h3 class="subtitle">Or, you can choose to simply watch one of the streams listed below!</h3>
      </div>
    </div>
  </section>
  <section class='section'>
    <div class='container'>
      <div v-for='stream in ytStreams' class='stream_search_result'>
        <div class='columns is-gapless'>
          <div class='column'>
            <router-link 
              :to="{ name : 'WatchYoutube', query : { watch : stream.stream_id } }">
              <img 
                v-bind:src=stream.thumbnail.url
                v-bind:height=stream.thumbnail.height
                v-bind:width=stream.thumbnail.width />
            </router-link>
          </div>
          <div class='column'>
            <router-link 
              :to="{ name : 'WatchYoutube', query : { watch : stream.stream_id } }">
              <p><h1 
               class='title'>{{ stream.stream_title }}</h1></p>
            </router-link>
            <p><h2 class='subtitle'>by {{ stream.channel_name }}</h2></p>
          </div>
        </div>
      </div>
    </div>
  </section>
</div>  
</template><!--}}}-->
<script> /* {{{ */
import Header from './Header'
import { mapState } from 'vuex'  

export default {  
  components: { // {{{
    'AppHeader': Header
  }, // }}}
  computed: // {{{
    mapState([ 
      'ytStreams', 'ytSearchTerm'
    ]), // }}}
  created() { // {{{
    this.$store.dispatch('repeatYoutubeSearch')
  } // }}}
} 
</script> /* }}} */
