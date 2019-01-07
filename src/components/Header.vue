<template>  <!--{{{-->
<nav class="navbar" role="navigation" aria-label="main navigation">  
  <span 
    v-bind:class="{ burger: true, 'navbar-burger': true, 'is-active': burgerActive }"
    v-on:click='burgerHandleClick'
    data-target='headerNavbarMenu'>
    <span></span>
    <span></span>
    <span></span>
  </span>
  <div v-bind:class="{'navbar-menu': true, 'is-active': navbarActive }" id='headerNavbarMenu'>
    <div class="navbar-start">
      <router-link to="/" class="navbar-item">
        Home
      </router-link>
    </div>
    <div class='navbar-item'>
      <SearchBar/>
    </div>
  </div>
</nav>  
</template> <!--}}}-->
<script> /* {{{ */
import SearchBar from './SearchBar'

export default {
  data() { // {{{
    return {
      burgerActive: false,
      navbarActive: false
    }
    
  }, // }}}
  components: { // {{{
    'SearchBar': SearchBar

  }, // }}}
  methods: { // {{{
    burgerHandleClick: function(event){
      this.burgerActive = !this.burgerActive
      this.navbarActive = !this.navbarActive
    }
  }, // }}}
  computed: { // {{{

  }, // }}}
  created() { // {{{
  } // }}}
}

</script> /* }}} */
<style> /* {{{ */
</style> /* }}} */
