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
      path: '/',
      name: 'Home',
      component: Home,
      beforeEnter(to, from, next){

        if(!store.getters.userLoggedIn && to.query.hasOwnProperty('code')){
          //console.log('bearer token found, dispatching')
          store.dispatch('authUser', to.query.code)
            .then((response) =>{
              //console.log('bearer token dispatched successfully')
              console.log(store.getters.userLoggedIn)
              next() 
            })
            .catch((error) => {
              next('/login')
            })

        } else if (!store.getters.userLoggedIn) {
          //console.log('user not logged in, pushing to login')
          next('login')
        } else {
          next() 
        }

      }
    },
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
    },
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
    },
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
    {
      path: '/errortest',
      name: 'ErrorTest',
      component: ErrorTest,
    },
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
  ]
})
