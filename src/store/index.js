// src/store/index.js

// {{{ Imports of Libraries
import Vue from 'vue'  
import Vuex from 'vuex'
// }}}

// Imports of AJAX Functions {{{
import { 
  fetchUserInfo, 
  authorizeUser,
  homePageSearchText } from '@/api'
// }}}

Vue.use(Vuex)

const state = {  //{{{
  // single source of data
  ytStreams: [],
  currentStream: {},
  userName: '',
  userEmail: '',
  userAvatar: '',
  userLoggedIn: false,
} //}}}

const actions = { // {{{
  // asynchronous operations
  loadUserInfo(context) { // {{{
    let jwt = localStorage.getItem('jwt')
    return new Promise((resolve, reject) => {
      //console.log("Fetching info...")
      fetchUserInfo(jwt).then(response => {
        //console.log("information found")

        if(response.data.loggedIn == true){
          context.commit('setUserName',   { name: response.data.name })
          context.commit('setUserEmail',  { email: response.data.email })
          context.commit('setUserAvatar', { avatar: response.data.avatar })
          context.commit('setUserLoggedInState', { loginState: true })
          resolve(response);
        }

        }, error => {
          console.log("USER INFO FETCH ERROR: ", error)
          reject(error);
        })
    })
  },

  // }}}
  authUser(context, authCode) { // {{{
    return new Promise((resolve, reject) => {
      authorizeUser(authCode)
      .then((response) => {
        //console.log("Authentication successful. Committing User Data to store")
        context.commit('setUserName',   { name: response.data.user.name })
        context.commit('setUserEmail',  { email: response.data.user.email })
        context.commit('setUserAvatar', { avatar: response.data.user.avatar })
        context.commit('setJWTToken',   { token: response.data.token }) 
        context.commit('setUserLoggedInState', { loginState: true })
        resolve(response)
      })
      .catch((error) => {
        console.log("AUTH ERROR: ", error)
        reject(error)
      })
    })
  }, 

  // }}}
  searchYoutube(context, search_text){ // {{{
    let jwt = localStorage.getItem('jwt')
    return new Promise((resolve, reject) => {
      homePageSearchText(search_text, jwt)
      .then((response) => {
        //console.log(response.data)
      })
      .catch((error) => {
        //console.log("SEARCH ERROR: ", error)
        reject(error)
      })
    })
  }, // }}}
} // }}}

const mutations = {  // {{{
  setUserName(state, payload){ // {{{
    //console.log('Setting Name: ', payload.name) 
    state.userName = payload.name
  }, /// }}}
  setUserLoggedInState(state, payload){ // {{{
    //console.log('Setting User Logged In State')
    state.userLoggedIn = payload.loginState
  }, // }}}
  setUserEmail(state, payload){ // {{{
    //console.log('Setting Email: ', payload.email) 
    state.userEmail = payload.email
  }, // }}}
  setUserAvatar(state, payload){ // {{{
    //console.log('Setting Avatar: ', payload.avatar) 
    state.userAvatar = payload.avatar
  }, // }}}
  setJWTToken(state, payload){ // {{{
    //console.log('Setting Token: ', payload) 
    localStorage.setItem('jwt', payload['token'])
  } // }}}
} // }}}

const getters = {  // {{{
  // reusable data accessors
} // }}}

const store = new Vuex.Store({ // {{{
  state,
  actions,
  mutations,
  getters
}) // {{{

export default store  

