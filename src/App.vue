<template>
  <div id="app">
    <router-view/>
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

// {{{ main options
$primary: hsl(0, 0%, 21%);
$background: hsl(0, 0%, 29%);
$title-color: hsl(0, 0%, 98%);
$body-color: hsl(0,0%,98%);

// }}}
// {{{ navbar options
$navbar-background-color: hsl(0,0%,29%);
$navbar-item-hover-background-color: hsl(0,0%,45%);
$navbar-item-color: hsl(0,0%,100%);
$navbar-item-hover-color: hsl(0,0%,100%);
// }}}

@import '~bulma/bulma';

html, body {
  height: 100%;
  background-color: hsl(0, 0%, 21%);
}
</style>
