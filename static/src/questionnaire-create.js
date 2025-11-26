// Remplacement de @babel/polyfill
import 'core-js/stable'
import 'regenerator-runtime/runtime'

import './utils/polyfills.js'

import { createApp } from 'vue'
import { loadStatuses, store } from './store'
import QuestionnaireCreate from './questionnaires/QuestionnaireCreate.vue'
import Sidebar from './utils/Sidebar.vue'

const controlsDataEl = typeof document !== 'undefined' ? document.getElementById('controls-data') : null
let controls = []
if (controlsDataEl && controlsDataEl.textContent && controlsDataEl.textContent.trim() !== '') {
  try {
    controls = JSON.parse(controlsDataEl.textContent)
  } catch (e) {
    console.error('questionnaire-create: failed to parse controls-data', e)
    controls = []
  }
} else {
  controls = []
}

// Helper to read bound attributes produced by Django templates. It handles
// variants like `:control-id="123"` or `control-id="123"` and converts to
// Number/Boolean when appropriate.
function readPropAttr(el, name) {
  if (!el) return undefined
  const candidates = [name, ':' + name, 'v-bind:' + name]
  for (const attr of candidates) {
    if (el.hasAttribute(attr)) {
      return el.getAttribute(attr)
    }
  }
  return undefined
}

// Commit server-injected controls early so that the QuestionnaireCreate
// component (mounted below) finds the data synchronously.
store.commit('updateControls', controls)
store.commit('updateControlsLoadStatus', loadStatuses.SUCCESS)

// Mount QuestionnaireCreate as a standalone app (runtime-only builds can't
// compile in-DOM templates like Vue 2 did), passing props read from the
// <questionnaire-create> element rendered by Django.
const questionnaireEl = typeof document !== 'undefined' ? document.querySelector('questionnaire-create') : null
let questionnaireProps = {}
if (questionnaireEl) {
  const controlIdRaw = readPropAttr(questionnaireEl, 'control-id')
  const questionnaireIdRaw = readPropAttr(questionnaireEl, 'questionnaire-id')
  const controlHasMultipleInspectorsRaw = readPropAttr(questionnaireEl, 'control-has-multiple-inspectors')
  const questionnaireNumberingRaw = readPropAttr(questionnaireEl, 'questionnaire-numbering')

  if (controlIdRaw !== undefined) {
    questionnaireProps.controlId = Number(controlIdRaw.replace(/"/g, ''))
  }
  if (questionnaireIdRaw !== undefined) {
    questionnaireProps.questionnaireId = Number(questionnaireIdRaw.replace(/"/g, ''))
  }
  if (controlHasMultipleInspectorsRaw !== undefined) {
    const val = controlHasMultipleInspectorsRaw.replace(/"/g, '')
    questionnaireProps.controlHasMultipleInspectors = (val === 'true' || val === 'True')
  }
  if (questionnaireNumberingRaw !== undefined) {
    questionnaireProps.questionnaireNumbering = Number(questionnaireNumberingRaw.replace(/"/g, ''))
  }
}

// Mount the main questionnaire app
const questionnaireApp = createApp(QuestionnaireCreate, questionnaireProps)
questionnaireApp.use(store)
questionnaireApp.mount('#questionnaire-create-vm')

// Mount the sidebar separately (it will reuse the same store)
const sidebarEl = typeof document !== 'undefined' ? document.getElementById('sidebar-vm') : null
if (sidebarEl) {
  const sidebarApp = createApp({ components: { Sidebar } })
  sidebarApp.use(store)
  sidebarApp.mount('#sidebar-vm')
}
