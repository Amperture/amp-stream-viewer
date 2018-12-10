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
import { faSearch } from '@fortawesome/free-solid-svg-icons'
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome'

library.add(faGoogle, faSearch)
Vue.component('font-awesome-icon', FontAwesomeIcon)
Vue.config.productionTip = false


// }}}
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
