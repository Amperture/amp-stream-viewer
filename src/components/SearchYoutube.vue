<template>  <!--{{{-->
<div>
<AppHeader/>
<section class='section'>
  <div class='container is-primary has-text-centered'>
    <h2 class='title'>Stream Search results for <strong>{{ ytSearchTerm }}</strong></h2>
  </div>
</section>
<section class='section'>
  <div class='columns'>
    <div class='column'
         v-for='stream in ytStreams'>
      <router-link
        :to="{ name : 'WatchYoutube', query : { watch : stream.stream_id } }">
        {{ stream.stream_title }} hosted by {{ stream.channel_name }}
        <img v-bind:src=stream.thumbnail />
      </router-link>
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
  created(){ // {{{
    //this.$store.dispatch('searchYoutube', this.search, this.sort)
  }, // }}}

  beforeMount(){
  }
}
</script> /* }}} */
