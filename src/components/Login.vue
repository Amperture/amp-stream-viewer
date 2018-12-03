<template>
<div>
  <section class="hero is-primary is-fullheight">
    <div class="hero-body">
      <div class="container has-text-centered">
        <h2 class="title">Welcome to Amp's YouTube Stream Viewer</h2>
        <h3 class="subtitle">Please Login to Get Started</h3>
        <a v-bind:href=google_auth class='button' id='googleSignInButton'><font-awesome-icon 
            :icon="['fab', 'google']" 
            pull="left" 
            fixed-width />Google Sign-In</a>
      </div>
    </div>
  </section>
</div>
</template>

<script>
export default{
  data() {
    return {
      google_auth: process.env.GOOGLE_AUTH_LINK
    }
  },
  beforeMount(){
  },
  components: {
  }, 
  computed: {
  },
  methods: {
  }
}

</script>

<style>
</style>
