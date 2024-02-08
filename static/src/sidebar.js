import '@babel/polyfill'
import './utils/polyfills.js'

import Sidebar from './utils/Sidebar.vue'
import { store } from './store'
import Vue from 'vue/dist/vue.js'
import Vuex from 'vuex'

Vue.use(Vuex)

new Vue({ // eslint-disable-line no-new
  el: '#sidebar-vm',
  store,
  components: {
    Sidebar,
  },
  mounted() {
    this.$store.dispatch('fetchSessionUser')
    console.log('fetch controls .....')
    this.$store.dispatch('fetchControls')
    this.$store.dispatch('fetchConfig')
  },
})
