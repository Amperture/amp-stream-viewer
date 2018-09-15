<template>
<div>
  <section class="hero is-primary is-fullheight">
    <div class="hero-body">
      <div class="container has-text-centered">
        <h2 class="title">Welcome to Amp's YouTube Stream Viewer</h2>
        <h3 class="subtitle">Please Login to Get Started</h3>
        <a class="button" id='googleSignInButton' v-on:click="signIn"><font-awesome-icon 
            :icon="['fab', 'google']" 
            pull="left" 
            fixed-width />Google Sign-In</a>
      </div>
    </div>
  </section>
</div>
</template>

<script>
import Vue from 'vue'

export default{
  components: {
  }, 
  computed: {
  },
  methods: {
    onSignInSuccess: function(authCode){
      console.log("SUCCESS!")
      console.log(authCode)
    },
    onSignInError: function (error){
      this.response = "Failed to Sign In"
      console.log("GOOGLE SIGN IN ERROR!", error)
      console.log(error)
    },
    signIn: function(){
      Vue.googleAuth().signIn(this.onSignInSuccess, this.onSignInError)
    }
  }
}

</script>

<style>
</style>
