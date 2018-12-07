<template>  <!--{{{-->
<div>
<AppHeader/>
  Hello World {{ this.$route.params.sortOrder }} {{ this.$route.params.searchTerm }}.
</div>
</template> <!--}}}-->
<script> /* {{{ */
import Header from './Header'

export default {
  components: { // {{{
    'AppHeader': Header
  }, // }}}

  beforeMount(){
    console.log("Am I mounted yet?")
    console.log(this.$route.params.sortOrder)
    console.log(this.$route.params.searchTerm)
  }
}
</script> /* }}} */
<style>
