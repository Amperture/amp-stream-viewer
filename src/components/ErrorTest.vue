<template>  <!--{{{-->
<div>
  <AppHeader/>
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
      errorPolling : null
    }

  }, // }}}
  computed: { // {{{

  }, // }}}
  methods: { // {{{ 


  }, // }}}
  beforeDestroy(){ // {{{
    // Disable chat polling.
    clearInterval(this.errorPolling)

  }, // }}}
  mounted(){ // {{{

  }, // }}}
  created(){ // {{{
    this.$store.dispatch('pollError')
      .then((response) => {
      })
      .catch((error) => {
        console.log(error)
      })
  } // }}}
}

</script> /* }}} */
<style> /* {{{ */
</style> /* }}} */
