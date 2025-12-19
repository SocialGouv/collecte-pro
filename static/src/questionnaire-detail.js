// Remplacement de @babel/polyfill
import 'core-js/stable'
import 'regenerator-runtime/runtime'
import './utils/polyfills.js'

import { createApp, h } from 'vue'
import QuestionnaireDetail from './questionnaires/QuestionnaireDetail.vue'
import { loadStatuses, store } from './store'

const controlsDataEl = typeof document !== 'undefined' ? document.getElementById('controls-data') : null
let controls = []
if (controlsDataEl && controlsDataEl.textContent && controlsDataEl.textContent.trim() !== '') {
  try {
    controls = JSON.parse(controlsDataEl.textContent)
  } catch (e) {
    console.error('questionnaire-detail: failed to parse controls-data', e)
    controls = []
  }
} else {
  controls = []
}

const questionnaireIdDataEl = typeof document !== 'undefined' ? document.getElementById('questionnaire-id-data') : null
let questionnaireId = NaN
if (questionnaireIdDataEl && questionnaireIdDataEl.textContent) {
  try {
    questionnaireId = Number(questionnaireIdDataEl.textContent.trim())
  } catch (e) {
    console.error('questionnaire-detail: failed to read questionnaire-id-data', e)
    questionnaireId = NaN
  }
}

const controlIdDataEl = typeof document !== 'undefined' ? document.getElementById('control-id-data') : null
let controlId = NaN
if (controlIdDataEl && controlIdDataEl.textContent) {
  try {
    controlId = Number(controlIdDataEl.textContent.trim())
  } catch (e) {
    console.error('questionnaire-detail: failed to read control-id-data', e)
    controlId = NaN
  }
}

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
