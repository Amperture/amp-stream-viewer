<template>  <!--{{{-->
<div>
<AppHeader/>
<section class='section'>
  <div class='container is-primary has-text-centered'>
    <h2 class='title'>Stream Search results for <strong>{{ ytSearchTerm }}</strong></h2>
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
</template> <!--}}}-->
<script> /* {{{ */
import Header from './Header'
import { mapState } from 'vuex'
 
export default {
  data(){ //{{{
    return {
      search: this.$route.query.search,
      sort: this.$route.query.sort
    }
  }, // }}}
  computed: // {{{
    mapState([
      'ytStreams', 'ytSearchTerm'
    ]), // }}}
  components: { // {{{
    'AppHeader': Header
  }, // }}}
}
</script> /* }}} */

