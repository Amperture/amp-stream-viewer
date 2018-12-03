<template>
<div>  
<AppHeader/>
  <section class="hero is-primary">
    <div class="hero-body">
      <div class="container has-text-centered">
        <h2 class="title">Search For YouTube Live Streams</h2>
        <form @submit.prevent="handleSearch">
          <input class="input has-text-centered" type="text" v-model="search_text" placeholder="What do you want to search for?"/></input>
        </form>
      </div>
    </div>
  </section>
</div>  
</template>

<script>
// {{{
import { mapState } from 'vuex'  
import Header from './Header'

export default {  
  components: { // {{{
    'AppHeader': Header
  }, // }}}

  computed: // {{{
    mapState({ 
      surveys: state => state.surveys
    }), // }}}

  methods: { // {{{
    handleSearch(){
      this.$store.dispatch('search_youtube', this.search_text)
        .then(response => {
        console.log("Search Executed!")
        })
    }
  }, // }}}

  data() { // {{{ 
    return {
      search_text: ''
    }
  }, // }}}

  beforeMount() { // {{{
  } // }}}
} // }}}
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
