import '@babel/polyfill'
import './utils/polyfills.js'

import { loadStatuses, store } from './store'
import QuestionnaireCreate from './questionnaires/QuestionnaireCreate.vue'
import Sidebar from './utils/Sidebar.vue'
import Vue from 'vue/dist/vue.js'
import Vuex, { mapActions } from 'vuex'

Vue.use(Vuex)

const controlsDataEl = document.getElementById('controls-data')
const controls = JSON.parse(controlsDataEl.textContent)

// Note : the parcel builds (build-questionnaire-create and watch-questionnaire-create) use
// --no-source-maps, because vuejs-datepicker breaks parcel without it.

// eslint-disable-next-line no-new
new Vue({
  store,
  el: '#questionnaire-create-vm',
  components: {
    QuestionnaireCreate,
    Sidebar,
  },
  methods: {
    ...mapActions(['fetchConfig', 'fetchControls', 'fetchSessionUser']),

  },
  created() {
    this.fetchConfig()
    this.fetchControls()
    this.$store.commit('updateControls', controls)
    this.$store.commit('updateControlsLoadStatus', loadStatuses.SUCCESS)
    this.fetchSessionUser()

  },
})
