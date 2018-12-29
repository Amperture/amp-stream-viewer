import Vue from 'vue'
import Router from 'vue-router'
import Home from '@/components/Home'
import Login from '@/components/Login'
import SearchYoutube from '@/components/SearchYoutube'
import WatchYoutube from '@/components/WatchYoutube'
import YoutubeStreamStats from '@/components/YoutubeStreamStats'

Vue.use(Router)

export default new Router({
  mode: 'history',
  routes: [
    {
      path: '/',
      name: 'Home',
      component: Home
    },
    {
      path: '/login',
      name: 'Login',
      component: Login
    },
    {
      path: '/ytwatch',
      name: 'WatchYoutube',
      component: WatchYoutube
    },
    {
      path: '/ytstats',
      name: 'YoutubeStreamStats',
      component: YoutubeStreamStats
    },
    {
      path: '/ytsearch',
      name: 'SearchYoutube',
      component: SearchYoutube
    }
  ]
})
