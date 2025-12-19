// Remplacement de @babel/polyfill
import 'core-js/stable'
import 'regenerator-runtime/runtime'
import './utils/polyfills.js'

import { createApp } from 'vue'
import { store, loadStatuses } from './store'
import QuestionnaireCreate from './questionnaires/QuestionnaireCreate.vue'
import Sidebar from './utils/Sidebar.vue'

// --- Récupération des données injectées côté serveur ---
const controlsDataEl = document.getElementById('controls-data')
let controls = []
if (controlsDataEl && controlsDataEl.textContent.trim() !== '') {
  try {
    controls = JSON.parse(controlsDataEl.textContent)
  } catch (e) {
    console.error('questionnaire-create: failed to parse controls-data', e)
    controls = []
  }
}
store.commit('updateControls', controls)
store.commit('updateControlsLoadStatus', loadStatuses.SUCCESS)

const userDataEl = document.getElementById('user-data')
if (userDataEl && userDataEl.textContent.trim() !== '') {
  try {
    const user = JSON.parse(userDataEl.textContent)
    store.commit('updateSessionUser', user)
    store.commit('updateSessionUserLoadStatus', loadStatuses.SUCCESS)
  } catch (e) {
    console.error('questionnaire-create: failed to parse user-data', e)
    store.dispatch('fetchSessionUser')
  }
} else {
  store.dispatch('fetchSessionUser')
}

// --- Helper pour lire les props bindées par Django ---
function readPropAttr(el, name) {
  if (!el) return undefined
  const candidates = [name, ':' + name, 'v-bind:' + name]
  for (const attr of candidates) {
    if (el.hasAttribute(attr)) return el.getAttribute(attr)
  }
  return undefined
}

// --- Montage du questionnaire ---
const questionnaireEl = document.querySelector('questionnaire-create')
if (questionnaireEl) {
  const props = {}
  const controlIdRaw = readPropAttr(questionnaireEl, 'control-id')
  const questionnaireIdRaw = readPropAttr(questionnaireEl, 'questionnaire-id')
  const controlHasMultipleInspectorsRaw = readPropAttr(questionnaireEl, 'control-has-multiple-inspectors')
  const questionnaireNumberingRaw = readPropAttr(questionnaireEl, 'questionnaire-numbering')

  if (controlIdRaw !== undefined) props.controlId = Number(controlIdRaw.replace(/"/g, ''))
  if (questionnaireIdRaw !== undefined) props.questionnaireId = Number(questionnaireIdRaw.replace(/"/g, ''))
  if (controlHasMultipleInspectorsRaw !== undefined) props.controlHasMultipleInspectors =
    controlHasMultipleInspectorsRaw.replace(/"/g, '') === 'true'
  if (questionnaireNumberingRaw !== undefined) props.questionnaireNumbering = Number(questionnaireNumberingRaw.replace(/"/g, ''))

  const questionnaireApp = createApp(QuestionnaireCreate, props)
  questionnaireApp.use(store)
  questionnaireApp.mount(questionnaireEl)
}

// --- Montage de la sidebar ---
const sidebarEl = document.getElementById('sidebar-vm')
if (sidebarEl) {
  const mountSidebar = () => {
    const sidebarApp = createApp(Sidebar)
    sidebarApp.use(store)
    sidebarApp.mount(sidebarEl)
  }

  // Si le sessionUser n’est pas encore chargé, attendre
  if (store.state.sessionUserLoadStatus === loadStatuses.LOADING) {
    const unwatch = store.watch(
      state => state.sessionUserLoadStatus,
      status => {
        if (status === loadStatuses.SUCCESS || status === loadStatuses.ERROR) {
          mountSidebar()
          unwatch()
        }
      }
    )
  } else {
    mountSidebar()
  }
}
