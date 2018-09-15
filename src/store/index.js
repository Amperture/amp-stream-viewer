// src/store/index.js

import Vue from 'vue'  
import Vuex from 'vuex'

// imports of ajax funcs go here
import { fetchUserInfo } from '@/api'

Vue.use(Vuex)

const state = {  
  // single source of data
  ytStreams: [],
  currentStream: {},
  user: {}
}

const actions = {  
  // asynchronous operations
  loadUserInfo(context) {
    console.log("Checking for user info...")
    return fetchUserInfo()
      .then((response) => {
        console.log(response.data)
        context.commit('setUser', { user: response })
      })
  }
}

const mutations = {  
  // isolated data mutations
  setUser(state, payload){
    state.user = payload.user
  }
}

const getters = {  
  // reusable data accessors
}

const store = new Vuex.Store({  
  state,
  actions,
  mutations,
  getters
})

export default store  

