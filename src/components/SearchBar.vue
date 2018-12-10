<template>  <!--{{{-->
  <div>
    <form @submit.prevent='handleSearch'>
      <div class='field is-horizontal'>
        <!-- Search Bar {{{ -->
        <div class='control is-expanded has-icons-right'>
          <input class='input' type='text' v-model='searchText' placeholder='Search...'>
          <span class='icon is-small is-right'>
            <font-awesome-icon icon='search'/>
          </span>
        </div> 
        <!-- Search Bar }}} -->
        <!-- Sort Order {{{ -->
        <div class='control is-fullwidth is-horizontal'>
          <div class='select'>
            <select v-model='selectedOrder'>
              <option 
                    v-for="order in orders"
                    v-bind:value='order.value'>
                {{ order.text }}
              </option>
            </select>
          </div>
        </div>
        <!-- Sort Order }}} -->
      </div>
    </form>
  </div>
</template> <!--}}}-->
<script> /* {{{ */
export default {
  data(){ // {{{
    return {
      selectedOrder: 'relevance',
      orders: [
        { 'text' : 'Date', 'value' : 'date' },
        { 'text' : 'Rating', 'value' : 'rating' },
        { 'text' : 'Relevance', 'value' : 'relevance' },
        { 'text' : 'Alphabetically by Title', 'value' : 'title' },
        { 'text' : 'Number of Viewers', 'value' : 'viewCount' }
      ],
      searchText: ''
    }
  }, // }}}
  methods: {//{{{
    handleSearch(){ // {{{
      //console.log(this.searchText, this.selectedOrder)
      this.$store.dispatch(
        'searchYoutube', 
        this.searchText, 
        this.selectedOrder)

      this.$router.push({
        name: 'SearchYoutube',
        /*
        query: {
          search: this.searchText,
          sort:  this.selectedOrder
        },
        */
      })
      /*
      this.$store.dispatch('searchYoutube', this.search_text)
        .then(response => {
        console.log("Search Executed!")
        })
      */
    }

  }, //}}}
}
</script> /* }}} */
