import { createApp } from 'vue'
import { store, loadStatuses } from './store'
import ControlDetail from './controls/ControlDetail.vue'

// Récupération des données du DOM (Django template) — guarded parsing to avoid crashes
const controlsDataEl = typeof document !== 'undefined' ? document.getElementById('controls-data') : null
const userDataEl = typeof document !== 'undefined' ? document.getElementById('user-data') : null

let controls = []
let user = {}
if (controlsDataEl && controlsDataEl.textContent && controlsDataEl.textContent.trim() !== '') {
  try {
    controls = JSON.parse(controlsDataEl.textContent)
  } catch (e) {
    console.error('control-detail: failed to parse controls-data', e)
    controls = []
  }
} else {
  controls = []
}

if (userDataEl && userDataEl.textContent && userDataEl.textContent.trim() !== '') {
  try {
    user = JSON.parse(userDataEl.textContent)
  } catch (e) {
    console.error('control-detail: failed to parse user-data', e)
    user = {}
  }
} else {
  user = {}
}

// Use the shared store so the sidebar and other entries read the same state.
// Commit the server-provided data into the shared store.
store.commit('updateControls', controls)
store.commit('updateControlsLoadStatus', loadStatuses.SUCCESS)
store.commit('updateSessionUser', user)
store.commit('updateSessionUserLoadStatus', loadStatuses.SUCCESS)
store.dispatch('fetchConfig')

// Création de l'app Vue
const app = createApp(ControlDetail, {
  control: controls[0] || null, // Passe le premier control si besoin
  user: user,
  accessType: 'demandeur' // ou dynamique selon contexte
})

app.use(store)
app.mount('#control-detail-vm')
