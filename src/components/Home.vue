<template>
<div>  
<AppHeader/>
  <section class="hero is-primary">
    <div class="hero-body">
      <div class="container has-text-centered">
        <h2 class="title">Search For YouTube Live Streams</h2>
        <input class="input has-text-centered" type="text" placeholder="What do you want to search for?"/></input>
      </div>
    </div>
  </section>
</div>  
</template>

<script>
import { mapState } from 'vuex'  
import Header from './Header'

export default {  
  components: {
    'AppHeader': Header
  },
  computed: mapState({
    surveys: state => state.surveys
  }),
  beforeMount() {
    this.$store.dispatch('loadUserInfo')
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
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
</style>
