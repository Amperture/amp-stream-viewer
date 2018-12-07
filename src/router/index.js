import Vue from 'vue'
import Router from 'vue-router'
import Home from '@/components/Home'
import StreamEmbed from '@/components/StreamEmbed'
import Login from '@/components/Login'
import SearchYoutube from '@/components/SearchYoutube'

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
      path: '/ytstream/:id',
      name: 'StreamEmbed',
      component: StreamEmbed
    },
    {
      path: '/ytsearch/:searchTerm/:sortOrder',
      name: 'SearchYoutube',
      component: SearchYoutube
    }
  ]
})
