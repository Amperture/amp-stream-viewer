<template> <!--{{{-->
<div>  
<AppHeader/>
  <section class="hero">
    <div class="hero-body">
      <div class="container has-text-centered">
        <h2 class="title">Search For YouTube Live Streams</h2>
        <h3 class="subtitle">Please use the search bar above to find a stream you would like to watch!</h3>
      </div>
    </div>
  </section>
</div>  
</template><!--}}}-->
<script> /* {{{ */
import { mapState } from 'vuex'  
import Header from './Header'

export default {  
  components: { // {{{
    'AppHeader': Header
  }, // }}}

  computed: // {{{
    mapState({ 
    }), // }}}

  methods: { // {{{
  }, // }}}

  data() { // {{{ 
    return {
      search_text: ''
    }
  }, // }}}

  beforeMount() { // {{{
  } // }}}
} 
</script> /* }}} */
<style scoped> /* {{{ */
h1, h2 {
  font-weight: normal;
}
ul {
  list-style-type: none;
  padding: 0;
}
li {
  display: inline-block;
  margin: 0 10px;
}
a {
  color: #42b983;
}
</style> /* }}} */
