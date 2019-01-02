// src/store/index.js

// {{{ Imports of Libraries
import Vue from 'vue'  
import Vuex from 'vuex'
// }}}

// Imports of AJAX Functions {{{
import { 
  fetchUserInfo, 
  fetchErrorTest, 
  authorizeUser,
  homePageSearchText,
  fetchChatMessages,
  fetchStreamStats,
  sendChatMessage,
  fetchStreamInfo } from '@/api'
// }}}

Vue.use(Vuex)

const state = {  //{{{
  // single source of data
  ytStreams: [],
  ytSearchTerm: '',
  currentStream: {},
  userName: '',
  userEmail: '',
  userAvatar: '',
  userLoggedIn: false,
} //}}}
const actions = { // {{{ 

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
  searchYoutube(context, {searchText, sortMethod}){ // {{{
    let jwt = localStorage.getItem('jwt')
    //console.log("SEARCH TEXT: ", searchText)
    //console.log("SORT METHOD: ", sortMethod)
    return new Promise((resolve, reject) => {
      homePageSearchText(searchText, sortMethod, jwt)
      .then((response) => {
        //console.log(response.data)
        context.commit('setJWTToken',   { token: response.data.jwt }) 
        context.commit('setStreamList', { 
          searchResult  :   response.data.searchResult,
          searchTerm    :   searchText
        }) 
      })
      .catch((error) => {
        console.log("SEARCH ERROR: ", error)
        reject(error)
      })
    })
  }, // }}}
  grabStreamInfo(context, videoID){ // {{{
    let jwt = localStorage.getItem('jwt')
    return new Promise((resolve, reject) => {
      fetchStreamInfo(videoID, jwt)
      .then((response) => {
        context.commit('setJWTToken',   { token: response.data.jwt }) 
        resolve(response.data)
      })
      .catch((error) => {
        console.log("CHAT ID ERROR: ", error)
        reject(error)
      })
    })
  }, // }}}
  grabStreamStats( // {{{
    context, 
    {
      videoID, 
      perPage, 
      page, 
      orderBy, 
      filtSponsors, 
      filtMods, 
      chatterNameSearch
    }
  ){ 
    let jwt = localStorage.getItem('jwt')
    return new Promise((resolve, reject) => {
      fetchStreamStats(
        videoID, perPage, page, orderBy, filtSponsors, 
        filtMods, chatterNameSearch, jwt
      )
      .then((response) => {
        //console.log(response.data)
        context.commit('setJWTToken',   { token: response.data.jwt }) 
        resolve(response.data)
      })
      .catch((error) => {
        console.log("STREAM STATS ERROR: ", error)
        reject(error)
      })
    })
  }, // }}}
  grabLiveChatMessages(context, {chatID, videoID, chatNextPageToken}){ // {{{
    let jwt = localStorage.getItem('jwt')
    //console.log("Action for Polling Chat Messages")
    //console.log("JWT: ", jwt)
    //console.log("ChatID: ", chatID)
    //console.log("ChatNextPageToken: ", chatNextPageToken)

    return new Promise((resolve, reject) => {
      fetchChatMessages(chatID, videoID, chatNextPageToken, jwt)
      .then((response) => {
        //console.log(response.data)
        context.commit('setJWTToken',   { token: response.data.jwt }) 
        resolve(response.data)
      })
      .catch((error) => {
        console.log("MESSAGES ERROR: ", error)
        reject(error)
      });

    });
  }, // }}}
  sendLiveChatMessage(context, {chatID, messageText}){ // {{{
    let jwt = localStorage.getItem('jwt')
    //console.log("Action for Polling Chat Messages")
    //console.log("JWT: ", jwt)
    //console.log("ChatID: ", chatID)
    //console.log("ChatNextPageToken: ", chatNextPageToken)

    return new Promise((resolve, reject) => {
      sendChatMessage(chatID, messageText, jwt)
      .then((response) => {
        console.log(response.data)
        context.commit('setJWTToken',   { token: response.data.jwt }) 
        resolve(response.data)
      })
      .catch((error) => {
        console.log("MESSAGES ERROR: ", error)
        reject(error)
      });

    });
  }, // }}}
  pollError(context){ // {{{
    return new Promise((resolve, reject) => {
      fetchErrorTest()
      .then((response) => {
        console.log(response.data)
        resolve(response.data)
      })
      .catch((error) => {
        console.log("MESSAGES ERROR")
        console.log("=====")
        console.log(error.response)
        console.log("=====")
        reject(error)
      });

    });
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
  }, // }}}
  setStreamList(state, payload){ // {{{
    //console.log('Setting Stream List: ', payload.search.items);
    state.ytStreams = [];
    state.ytSearchTerm = payload.searchTerm;
    let streamList = payload.searchResult.items;
    for(var i in streamList){
      state.ytStreams.push({
        'stream_id' : streamList[i].id.videoId,
        'channel_name' : streamList[i].snippet.channelTitle,
        'stream_description' : streamList[i].snippet.description,
        'stream_title' : streamList[i].snippet.title,
        'thumbnail' : streamList[i].snippet.thumbnails.high.url
      })
    }
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
}) // }}}

export default store  

