// Remplacement de @babel/polyfill
import 'core-js/stable'
import 'regenerator-runtime/runtime'

import './utils/polyfills.js'

import { loadStatuses, store } from './store'
import QuestionnaireCreate from './questionnaires/QuestionnaireCreate.vue'
import Sidebar from './utils/Sidebar.vue'
import { createApp } from 'vue'

// Récupération des controls injectés par le serveur
const controlsDataEl = document.getElementById('controls-data')
let controls = []
if (controlsDataEl && controlsDataEl.textContent && controlsDataEl.textContent.trim() !== '') {
  try {
    controls = JSON.parse(controlsDataEl.textContent)
  } catch (e) {
    console.error('questionnaire-create: failed to parse controls-data', e)
    controls = []
  }
}

// Commit server-injected controls dans le store
store.commit('updateControls', controls)
store.commit('updateControlsLoadStatus', loadStatuses.SUCCESS)

// Helper pour lire les props bindées par Django
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

// Montage du questionnaire
const questionnaireEl = document.querySelector('questionnaire-create')
if (questionnaireEl) {
  let props = {}

  const controlIdRaw = readPropAttr(questionnaireEl, 'control-id')
  const questionnaireIdRaw = readPropAttr(questionnaireEl, 'questionnaire-id')
  const controlHasMultipleInspectorsRaw = readPropAttr(questionnaireEl, 'control-has-multiple-inspectors')
  const questionnaireNumberingRaw = readPropAttr(questionnaireEl, 'questionnaire-numbering')

  if (controlIdRaw !== undefined) props.controlId = Number(controlIdRaw.replace(/"/g, ''))
  if (questionnaireIdRaw !== undefined) props.questionnaireId = Number(questionnaireIdRaw.replace(/"/g, ''))
  if (controlHasMultipleInspectorsRaw !== undefined) {
    const val = controlHasMultipleInspectorsRaw.replace(/"/g, '')
    props.controlHasMultipleInspectors = val === 'true' || val === 'True'
  }
  if (questionnaireNumberingRaw !== undefined) props.questionnaireNumbering = Number(questionnaireNumberingRaw.replace(/"/g, ''))

  const questionnaireApp = createApp(QuestionnaireCreate, props)
  questionnaireApp.use(store)
  questionnaireApp.mount(questionnaireEl)
}

// Montage de la sidebar
const sidebarEl = document.getElementById('sidebar-vm')
if (sidebarEl) {
  const sidebarApp = createApp(Sidebar)
  sidebarApp.use(store)
  sidebarApp.mount(sidebarEl)
}
