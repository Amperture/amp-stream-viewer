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
  beforeDestroy(){ // {{{
    // Disable chat polling.
    clearInterval(this.errorPolling)

  }, // }}}
  created(){ // {{{
    this.$store.dispatch('pollError')
      .catch((error) => {
        console.log(error)
      })
  } // }}}
}

</script> /* }}} */
