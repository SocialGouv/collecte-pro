// Remplacement de @babel/polyfill
import 'core-js/stable'
import 'regenerator-runtime/runtime'
import './utils/polyfills.js'

import { createApp, h } from 'vue'
import QuestionnaireDetail from './questionnaires/QuestionnaireDetail.vue'
import { loadStatuses, store } from './store'

const controlsDataEl = document.getElementById('controls-data')
const controls = JSON.parse(controlsDataEl.textContent)

const questionnaireIdDataEl = document.getElementById('questionnaire-id-data')
const questionnaireId = Number(questionnaireIdDataEl.textContent.trim())

const controlIdDataEl = document.getElementById('control-id-data')
const controlId = Number(controlIdDataEl.textContent.trim())

const app = createApp({
  render: () => h(QuestionnaireDetail, {
    controlId,
    questionnaireId
  }),
  mounted() {
    this.fetchConfig()
    this.fetchSessionUser()
    this.$store.commit('updateControls', controls)
    this.$store.commit('updateControlsLoadStatus', loadStatuses.SUCCESS)
  },
  methods: {
    fetchConfig() {
      this.$store.dispatch('fetchConfig')
    },
    fetchSessionUser() {
      this.$store.dispatch('fetchSessionUser')
    }
  }
})

app.use(store)
app.mount('#questionnaire-detail-app')
