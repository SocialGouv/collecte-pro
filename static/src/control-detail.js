import { createApp } from 'vue'
import { createStore } from 'vuex'
import ControlDetail from './controls/ControlDetail.vue'

// Récupération des données du DOM (Django template)
const controlsDataEl = document.getElementById('controls-data')
const userDataEl = document.getElementById('user-data')

const controls = JSON.parse(controlsDataEl.textContent)
const user = JSON.parse(userDataEl.textContent)

// Store minimal pour ControlDetail
const store = createStore({
  state: {
    controls: [],
    sessionUser: null,
    loadStatus: {}
  },
  mutations: {
    updateControls(state, controlsData) {
      state.controls = controlsData
    },
    updateSessionUser(state, userData) {
      state.sessionUser = userData
    },
    updateControlsLoadStatus(state, status) {
      state.loadStatus.controls = status
    },
    updateSessionUserLoadStatus(state, status) {
      state.loadStatus.user = status
    }
  },
  actions: {
    async fetchConfig() {
      // Implémenter si besoin, sinon peut rester vide
      return
    }
  }
})

// Création de l'app Vue
const app = createApp(ControlDetail, {
  control: controls[0] || null, // Passe le premier control si besoin
  user: user,
  accessType: 'demandeur' // ou dynamique selon contexte
})

app.use(store)
app.mount('#control-detail-vm')
