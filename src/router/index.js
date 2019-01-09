import Vue from 'vue'
import Router from 'vue-router'
import Home from '@/components/Home'
import Login from '@/components/Login'
import SearchYoutube from '@/components/SearchYoutube'
import WatchYoutube from '@/components/WatchYoutube'
import YoutubeStreamStats from '@/components/YoutubeStreamStats'
import ErrorTest from '@/components/ErrorTest'

import store from '@/store/index.js'

Vue.use(Router)

export default new Router({
  mode: 'history',
  routes: [
    {
      // Home Page Path {{{
      path: '/',
      name: 'Home',
      component: Home,
      beforeEnter(to, from, next){
        // The Home Route will end up being the one intercepting the OAuth
        // Code from Google. So a more complex check will need to be done.

        if(!store.getters.userLoggedIn && to.query.hasOwnProperty('code')){
          //console.log("code")
          store.dispatch('authUser', to.query.code)

            .then((response) =>{
              let token = response.data.token
              let expRaw = JSON.parse(atob(token.split('.')[1])).exp
              let exp = new Date(expRaw * 1000)
              let now = new Date()
              now < exp ? next() : next('login');
            })

            .catch((error) => {
              next('login')
            })

        } else if (!store.getters.userLoggedIn) {
          next('login')
        } else {
          next() 
        }

      }
    }, // }}}
    // Login Path {{{
    {
      path: '/login',
      name: 'Login',
      component: Login,
      beforeEnter(to, from, next){
        if(store.getters.userLoggedIn){
          next('/')
        } else {
          next() 
        }
      }
    }, // }}}
    // Stream Watch Page Route {{{
    {
      path: '/ytwatch',
      name: 'WatchYoutube',
      component: WatchYoutube,
      beforeEnter(to, from, next){
        if(!store.getters.userLoggedIn){
          next('/login')
        } else {
          next() 
        }
      }
    }, // }}}
    // Stream Stats Page Route {{{
    {
      path: '/ytstats',
      name: 'YoutubeStreamStats',
      component: YoutubeStreamStats,
      beforeEnter(to, from, next){
        if(!store.getters.userLoggedIn){
          next('/login')
        } else {
          next() 
        }
      }
    },
    // }}}
    // Error Test Route {{{
    {
      path: '/errortest',
      name: 'ErrorTest',
      component: ErrorTest,
    },
    // }}}
    // Youtube Search Route {{{
    {
      path: '/ytsearch',
      name: 'SearchYoutube',
      component: SearchYoutube,
      beforeEnter(to, from, next){
        if(!store.getters.userLoggedIn){
          next('/login')
        } else {
          next() 
        }
      }
    } 
    // }}}
  ]
})
