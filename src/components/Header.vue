<template>  
<nav class="navbar is-black" role="navigation" aria-label="main navigation">  
  <div class="navbar-menu">
    <div class="navbar-start">
      <router-link to="/" class="navbar-item">
        Home
      </router-link>
    </div>
  </div>
</nav>  
</template>

<script>  
export default {
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

</script>

<style>  
</style>  
