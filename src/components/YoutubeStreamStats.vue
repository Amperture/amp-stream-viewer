<template>  <!--{{{-->
<div>
  <AppHeader/>
  <!-- Stream Title/Streamer Section {{{ -->
  <section class='section is-small'> 
    <div class='container'>
      <h1 class='title'>Stats For: {{ streamTitle }}</h1>
      <h2 class='subtitle'>by {{ streamerName }}</h2>
    </div> 
  </section>
  <!-- Title Section }}}-->
  <p>TOTAL CHATTERS: {{ numChatters }}</p>
  <!-- Filtering Section {{{ -->
  <div v-if='filterShow == true'>
    <!-- Sponsor/Mod Filter {{{ -->

    <div class="field"> 
      <label class="label">Sponsors/Members</label>
      <div class="control">
        <div class="select">
          <select v-model='filtSponsors' v-on:change='changePages(1)'>
            <option
              v-for='option in filtSponsorOptions'
              v-on:change='changePages(1)'
              v-bind:value='option.value'>{{ option.text }}</option>
          </select>
        </div>
      </div> 
      <label class="label">Moderators</label>
      <div class="control">
        <div class="select">
          <select v-model='filtMods' v-on:change='changePages(1)'>
            <option
              v-for='option in filtModOptions'
              v-bind:value='option.value'>{{ option.text }}</option>
          </select>
        </div>
      </div>
    </div>

    <!-- Sponsor/Mod Filter }}} -->
    <!-- Order By Setting {{{ -->


    <div class="field"> 
      <label class="label">Order By:</label>
      <div class="control">
        <div class="select">
          <select v-model='orderBy' v-on:change='changePages(1)'>
            <option
              v-for='option in orderOptions'
              v-on:change='changePages(1)'
              v-bind:value='option.value'>{{ option.text }}</option>
          </select>
        </div>
      </div> 
    </div>

    <!-- Order By Setting }}} -->
    
    <button 
      class='button is-primary' 
      v-on:click='filterShow = !filterShow'>Hide Advanced Filters</button>

  </div>
  <div v-if='filterShow == false'>
    <button 
      class='button is-primary' 
      v-on:click='filterShow = !filterShow'>Show Advanced Filters</button>
  </div>

  <!-- Filtering Section }}} -->
  <!-- Chatters Section {{{-->

  <!-- Chatters Table {{{-->

  <table class='table'> 
    <thead>
      <tr>
        <th><abbr title='User Avatar'>
            <span class='icon is-small'> 
              <font-awesome-icon icon='user-circle'/>
            </span>
          </abbr></th>
        <th><abbr title='Moderator Status'>
            <span class='icon is-small'> 
              <font-awesome-icon icon='wrench'/>
            </span>
          </abbr></th>
        <th><abbr title='Sponsor Status'>
            <span class='icon is-small'> 
              <font-awesome-icon icon='money-bill-wave'/>
            </span>
          </abbr></th>
        <th>Name <abbr title="Chatter's Account Name">?</abbr></th>
        <th>Messages <abbr title='Number of Messages by Chatter'>?</abbr></th>
      </tr>
    </thead>
    <tbody>
      <tr v-for='x in chatActivityRank'>
        <td>
          <figure class='image is-32x32'> <img class='is-rounded' v-bind:src='x.avatar'/> </figure>
        </td>
        <td>
          <span class='icon is-small' v-if='x.isMod == true'> 
            <font-awesome-icon icon='wrench'/>
          </span>
        </td>
        <td>
          <span class='icon is-small' v-if='x.isSponsor == true'> 
            <font-awesome-icon icon='money-bill-wave'/>
          </span>
        </td>
        <td> {{ x.name }} </td>
        <td> {{ x.numMessages }} </td>
      </tr>
    </tbody>
  </table>

  <!-- Chatters Table }}}-->
  <!-- Chatters Pagination {{{-->

  <div v-if='numPages > 1'>
    <nav class="pagination" role="navigation" aria-label="pagination">
      <ul class="pagination-list">
        <li v-if='page != 1'>
          <button 
            class="pagination-link" 
            aria-label="Goto page 1" 
            v-on:click='changePages(1)'>1</button>
        </li>
        <li v-if='page != 1'>
          <span class="pagination-ellipsis">&hellip;</span>
        </li>
        <li v-if='page != 1'>
          <button 
            class="pagination-link" 
            aria-label="Goto previous page"
            v-on:click='changePages(page - 1)'>{{ page - 1 }}</button>
        </li>
        <li>
          <button 
            class="pagination-link is-current" 
            aria-label="Page 46" 
            aria-current="page">{{ page }}</button>
        </li>
        <li v-if='page != numPages'>
          <button 
            class="pagination-link" 
            aria-label="Goto next page"
            v-on:click='changePages(page + 1)'>{{ page + 1 }}</button>
        </li>
        <li v-if='page != numPages'>
          <span class="pagination-ellipsis">&hellip;</span>
        </li>
        <li v-if='page != numPages'>
          <button 
            class="pagination-link" 
            aria-label="Goto last page"
            v-on:click='changePages(numPages)'>{{ numPages }}</button>
        </li>
      </ul>
    </nav>
  </div>

  <!-- Chatters Pagination }}}-->

  <!-- Chatters Section }}}-->
</div>
</template> <!--}}}-->
<script> /* {{{ */

import Header from './Header'

export default {
  components: { // {{{
    'AppHeader' : Header

  }, // }}}
  data() { // {{{ 

    return {
      streamID            : this.$route.query.watch, 
      numChatters         : 0,
      numChattersFilt     : 0,
      statsPollTiming     : 10000, // ms, 1000 = 1 second
      statsPollInterval   : null,
      chatActivityRank    : [],
      streamTitle         : '',
      streamerName        : '',

      perPage             : 10,
      page                : 1, // Showing as Page 1, will subtract 1 when 
                               // making API call.
      // Ordering Options {{{

      orderBy             : 'numMessages desc',
      orderOptions        : [
        { 'text' : 'Name, A-Z', 'value' : 'name' },
        { 'text' : 'Name, Z-A', 'value' : 'name desc' },
        { 
            'text'  : 'Number of Messages, Most First', 
            'value' : 'numMessages desc' 
        },
        { 
            'text'  : 'Number of Messages, Least First', 
            'value' : 'numMessages' 
        }
      ],

      // }}}
      // Sponsor Filters {{{

      filtSponsors        : 'include',
      filtSponsorOptions  : [
        { 'text' : 'Include', 'value' : 'include' },
        { 'text' : 'Exclude', 'value' : 'exclude' },
        { 'text' : 'Show Only', 'value' : 'only' }
      ],

      // }}}
      // Moderator Filters {{{
      filtMods            : 'include',
      filtModOptions  : [
        { 'text' : 'Include', 'value' : 'include' },
        { 'text' : 'Exclude', 'value' : 'exclude' },
        { 'text' : 'Show Only', 'value' : 'only' }
      ],
      // }}}
      filterShow          : false

    }

  }, // }}}
  computed: { // {{{

    numPages: function () { // {{{
      return Math.ceil(this.numChattersFilt / this.perPage)
    } // }}}

  }, // }}}
  methods: { // {{{ 

    pollStreamStats(){// {{{

      this.$store.dispatch('grabStreamStats', {
        videoID       : this.streamID,
        perPage       : this.perPage,
        page          : this.page,
        orderBy       : this.orderBy,
        filtSponsors  : this.filtSponsors,
        filtMods      : this.filtMods
      })
        .then((response) => {
          this.numChatters = response.numChatters
          this.numChattersFilt = response.numChattersFilt
          this.streamTitle = response.streamTitle
          this.streamerName = response.streamerName
          this.chatActivityRank = response.chatActivityRank
        })
        .catch((error) => {
        })

    }, // }}}
    changePages(pageToMoveTo){// {{{
      this.page = pageToMoveTo
      this.pollStreamStats()
    }, // }}}

  }, // }}}
  beforeDestroy(){ // {{{

    clearInterval(this.statsPollInterval)

  }, // }}}
  mounted(){ // {{{

  }, // }}}
  created(){ // {{{

    // Setup Stats Interval
    this.pollStreamStats()
    this.statsPollInterval = setInterval(() => {
      this.pollStreamStats()
    }, this.statsPollTiming)

  } // }}}
  }

</script> /* }}} */
<style> /* {{{ */
</style> /* }}} */
