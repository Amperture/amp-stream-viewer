<template>
  <div id="app">
    <transition 
      name='router-anim'
      enter-active-class='animated slideInRight'
      leave-active-class='animated slideOutRight'>
      <router-view/>
    </transition>
  </div>
</template>

<script>
export default {
  name: 'App',
  components: {
  }
}
</script>

<style lang="scss">
@import "~bulmaswatch/superhero/_variables.scss";
@import '~bulma/bulma';
@import "~bulmaswatch/superhero/_overrides.scss";
</style>
<style>
@import "https://cdn.jsdelivr.net/npm/animate.css@3.5.1";
</style>
