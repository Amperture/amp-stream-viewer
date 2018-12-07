<template>  <!--{{{-->
<nav class="navbar is-black" role="navigation" aria-label="main navigation">  
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
      console.log("BURGER CLICKED!")
      this.burgerActive = !this.burgerActive
      this.navbarActive = !this.navbarActive
    }
  }, // }}}
  computed: { // {{{

  }, // }}}
  beforeMount() { // {{{
    var authCodeReceived = (this.$route.query.code != undefined)
    switch( authCodeReceived + "|" + this.$store.state.userLoggedIn ){
      case 'true|false' : //{{{
      case 'true|true'  : 
        console.log("Auth Code Found, sending to API server...")

        this.$store.dispatch('authUser', this.$route.query.code)
          .then(response => {
            console.log("User logged in successfully!")
          }, error => {
            console.log("Something went wrong!")
            this.$router.push('login')
            console.log(error)
          }) 

        break; // }}} 
      case 'false|false' : // {{{
        console.log("User not initially logged in. Checking Token...")

        this.$store.dispatch('loadUserInfo').then(response => {
          if(this.$store.state.userLoggedIn == true){
            console.log("User has valid token, info loaded.")
          }
        }, error => {
          console.log("Login Token Invalid, Sending to Login")
          this.$router.push('login')
        }) 

        break; 
      case 'false|true':
        console.log("User Logged In, No need for anything else.")
    } // }}}
  } // }}}
}

</script> /* }}} */
<style> /* {{{ */
$navbar-background-color: hsl(0,0%,29%);
$navbar-item-hover-background-color: hsl(0,0%,45%);
$navbar-item-color: hsl(0,0%,100%);
$navbar-item-hover-color: hsl(0,0%,100%);
</style> /* }}} */
