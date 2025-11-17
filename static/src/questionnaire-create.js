// Remplacement de @babel/polyfill
import 'core-js/stable'
import 'regenerator-runtime/runtime'

import './utils/polyfills.js'

import { createApp } from 'vue'
import { loadStatuses, store } from './store'
import QuestionnaireCreate from './questionnaires/QuestionnaireCreate.vue'
import Sidebar from './utils/Sidebar.vue'

const controlsDataEl = document.getElementById('controls-data')
const controls = JSON.parse(controlsDataEl.textContent)

const app = createApp({
  components: {
    QuestionnaireCreate,
    Sidebar,
  },
  mounted() {
    this.fetchConfig()
    this.fetchControls()
    this.$store.commit('updateControls', controls)
    this.$store.commit('updateControlsLoadStatus', loadStatuses.SUCCESS)
    this.fetchSessionUser()
  },
  methods: {
    fetchConfig() {
      this.$store.dispatch('fetchConfig')
    },
    fetchControls() {
      this.$store.dispatch('fetchControls')
    },
    fetchSessionUser() {
      this.$store.dispatch('fetchSessionUser')
    },
  },
})

app.use(store)
app.mount('#questionnaire-create-vm')
