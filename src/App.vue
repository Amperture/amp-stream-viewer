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

$primary: hsl(0, 0%, 21%);
$background: hsl(0, 0%, 29%);

@import '~bulma/bulma';

html, body {
  height: 100%;
  background-color: hsl(0, 0%, 21%);
}
</style>
