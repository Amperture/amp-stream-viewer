// The Vue build version to load with the `import` command
// (runtime-only or standalone) has been set in webpack.base.conf with an alias.

// {{{ Component imports
import Vue from 'vue'
import App from './App'
import router from './router'
import store from './store'

// }}}
// {{{ Fontawesome imports and config
import { library } from '@fortawesome/fontawesome-svg-core'
import { faGoogle } from '@fortawesome/free-brands-svg-icons'
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome'
library.add(faGoogle)
Vue.component('font-awesome-icon', FontAwesomeIcon)
Vue.config.productionTip = false

// }}}
// {{{ Google Auth Imports and Config
/*
import GoogleAuth from 'vue-google-oauth'
Vue.use(GoogleAuth, {
  client_id: process.env.GOOGLE_OAUTH_CLIENT_ID,
  scope: 'profile email https://www.googleapis.com/auth/youtube.force-ssl https://www.googleapis.com/auth/youtube'
})
Vue.googleAuth().load()
*/

//}}} 
//{{{ App Entry
/* eslint-disable no-new */
new Vue({
  el: '#app',
  router,
  store,
  components: { App },
  template: '<App/>'
})

//}}}
