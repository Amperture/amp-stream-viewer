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
      streamID : this.$route.query.watch,
    }
  }, // }}}
  computed: {
    youtubeEmbedURL : function() {
      return 'https://www.youtube.com/embed/' + this.streamID;
    }
  },
  beforeMount(){ // {{{
    console.log(this.streamID)
    console.log(this.youtubeEmbedURL)
  } // }}}
}

</script> /* }}} */

