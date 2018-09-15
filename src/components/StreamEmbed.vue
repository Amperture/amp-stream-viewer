<template>
<div>
<!-- TitleBar Section {{{-->
  <section class="hero is-primary is-small">
    <div class="hero-body">
      <div class="container has-text-centered">
        <h2 class="title">{{ ytStream.name }}</h2>
      </div>
    </div>
  </section>
  <!-- TitleBar Section }}}-->
  <section class="section">
    <div class="container">
      <div class="columns">
        <div class="column is-two-thirds">
          <iframe width="100%" height="480px" :src="ytStream.embedURL" allowfullscreen></iframe>
        </div>
        <div class="column">
          <table class="table is-fullwidth is-scrollable" height="480px">
            <tbody>
              <td>Avatar</td>
              <td>Username</td>
              <td>Message</td>
            </tbody>
            <tbody>
              <td>Avatar</td>
              <td>Username</td>
              <td>Message</td>
            </tbody>
            <tbody>
              <td>Avatar</td>
              <td>Username</td>
              <td>Message</td>
            </tbody>
            <tbody>
              <td>Avatar</td>
              <td>Username</td>
              <td>Message</td>
            </tbody>
            <tbody>
              <td>Avatar</td>
              <td>Username</td>
              <td>Message</td>
            </tbody>
            <tbody>
              <td>Avatar</td>
              <td>Username</td>
              <td>Message</td>
            </tbody>
            <tbody>
              <td>Avatar</td>
              <td>Username</td>
              <td>Message</td>
            </tbody>
            <tbody>
              <td>Avatar</td>
              <td>Username</td>
              <td>Message</td>
            </tbody>
            <tbody>
              <td>Avatar</td>
              <td>Username</td>
              <td>Message</td>
            </tbody>
            <tbody>
              <td>Avatar</td>
              <td>Username</td>
              <td>Message</td>
            </tbody>
            <tbody>
              <td>Avatar</td>
              <td>Username</td>
              <td>Message</td>
            </tbody>
            <tbody>
              <td>Avatar</td>
              <td>Username</td>
              <td>Message</td>
            </tbody>
            <tbody>
              <td>Avatar</td>
              <td>Username</td>
              <td>Message</td>
            </tbody>
            <tbody>
              <td>Avatar</td>
              <td>Username</td>
              <td>Message</td>
            </tbody>
            <tbody>
              <td>Avatar</td>
              <td>Username</td>
              <td>Message</td>
            </tbody>
            <tbody>
              <td>Avatar</td>
              <td>Username</td>
              <td>Message</td>
            </tbody>
            <tbody>
              <td>Avatar</td>
              <td>Username</td>
              <td>Message</td>
            </tbody>
            <tbody>
              <td>Avatar</td>
              <td>Username</td>
              <td>Message</td>
            </tbody>
            <tbody>
              <td>Avatar</td>
              <td>Username</td>
              <td>Message</td>
            </tbody>
            <tbody>
              <td>Avatar</td>
              <td>Username</td>
              <td>Message</td>
            </tbody>
            <tbody>
              <td>Avatar</td>
              <td>Username</td>
              <td>Message</td>
            </tbody>
            <tbody>
              <td>Avatar</td>
              <td>Username</td>
              <td>Message</td>
            </tbody>
            <tbody>
              <td>Avatar</td>
              <td>Username</td>
              <td>Message</td>
            </tbody>
            <tbody>
              <td>Avatar</td>
              <td>Username</td>
              <td>Message</td>
            </tbody>
            <tbody>
              <td>Avatar</td>
              <td>Username</td>
              <td>Message</td>
            </tbody>
            <tbody>
              <td>Avatar</td>
              <td>Username</td>
              <td>Message</td>
            </tbody>
            <tbody>
              <td>Avatar</td>
              <td>Username</td>
              <td>Message</td>
            </tbody>
            <tbody>
              <td>Avatar</td>
              <td>Username</td>
              <td>Message</td>
            </tbody>
            <tbody>
              <td>Avatar</td>
              <td>Username</td>
              <td>Message</td>
            </tbody>
            <tbody>
              <td>Avatar</td>
              <td>Username</td>
              <td>Message</td>
            </tbody>
            <tbody>
              <td>Avatar</td>
              <td>Username</td>
              <td>Message</td>
            </tbody>
            <tbody>
              <td>Avatar</td>
              <td>Username</td>
              <td>Message</td>
            </tbody>
            <tbody>
              <td>Avatar</td>
              <td>Username</td>
              <td>Message</td>
            </tbody>
            <tbody>
              <td>Avatar</td>
              <td>Username</td>
              <td>Message</td>
            </tbody>
            <tbody>
              <td>Avatar</td>
              <td>Username</td>
              <td>Message</td>
            </tbody>
            <tbody>
              <td>Avatar</td>
              <td>Username</td>
              <td>Message</td>
            </tbody>
            <tbody>
              <td>Avatar</td>
              <td>Username</td>
              <td>Message</td>
            </tbody>
            <tbody>
              <td>Avatar</td>
              <td>Username</td>
              <td>Message</td>
            </tbody>
            <tbody>
              <td>Avatar</td>
              <td>Username</td>
              <td>Message</td>
            </tbody>
            <tbody>
              <td>Avatar</td>
              <td>Username</td>
              <td>Message</td>
            </tbody>
            <tbody>
              <td>Avatar</td>
              <td>Username</td>
              <td>Message</td>
            </tbody>
            <tbody>
              <td>Avatar</td>
              <td>Username</td>
              <td>Message</td>
            </tbody>
            <tbody>
              <td>Avatar</td>
              <td>Username</td>
              <td>Message</td>
            </tbody>
          </table> 
        </div>
      </div>
    </div>
  </section>
</div>
</template>

<script>  
export default {  
  data() {
    return {
      ytStream: {
        name: "Watch this now!",
        streamID: "hHW1oY26kxQ",
        embedURL: "https://www.youtube.com/embed/hHW1oY26kxQ"
      }
    }
  },
  beforeMount() {
  }, 
  methods: { //{{{
  }, //}}}
  computed: {  // new Vue obj member{{{
  }//}}}
}
</script>

<style>
.table.is-scrollable tbody { 
  overflow-y: scroll;
  width: auto;
}
</style>
