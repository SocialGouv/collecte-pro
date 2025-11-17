import axios from 'axios'
// L'importation de getField et updateField est supprimée
import backendUrls from './utils/backend.js'
// Vue n'est plus importé ni utilisé globalement
import { createStore } from 'vuex' // Importation de la nouvelle fonction createStore de Vuex 4

// La syntaxe des états de chargement est conservée
export const loadStatuses = {
  LOADING: Symbol('LOADING'),
  SUCCESS: Symbol('SUCCESS'),
  ERROR: Symbol('ERROR'),
}

// export const store = new Vuex.Store({  <-- Ancienne syntaxe
export const store = createStore({ // Nouvelle syntaxe Vuex 4
  state: {
    config: {},
    configLoadStatus: loadStatuses.LOADING,
    controls: [],
    controlsLoadStatus: loadStatuses.LOADING,
    currentQuestionnaire: {},
    editingControl: {},
    editingUser: {},
    editingProfileType: '',
    sessionUser: {},
    sessionUserLoadStatus: loadStatuses.LOADING,
  },
  // La méthode getField est supprimée
  getters: {
    // Les getters natifs peuvent être ajoutés ici si nécessaire, 
    // mais le getter 'getField' de vuex-map-fields n'est plus requis.
  },
  mutations: {
    // updateField est supprimé. Les mutations sont ajoutées pour les champs qui étaient gérés par mapFields

    // Mutations spécifiques pour remplacer mapFields (ajoutées pour les besoins des composants migrés)
    setEditingControl(state, payload) {
      state.editingControl = payload
    },
    setEditingUser(state, payload) {
      state.editingUser = payload
    },
    setEditingProfileType(state, payload) {
      state.editingProfileType = payload
    },

    // Mutations existantes et conservées
    updateSessionUser(state, user) {
      state.sessionUser = user
    },
    updateSessionUserLoadStatus(state, newStatus) {
      state.sessionUserLoadStatus = newStatus
    },
    updateConfig(state, config) {
      state.config = config
    },
    updateConfigLoadStatus(state, newStatus) {
      state.configLoadStatus = newStatus
    },
    updateControls(state, controls) {
      state.controls = controls
    },
    updateControlsLoadStatus(state, newStatus) {
      state.controlsLoadStatus = newStatus
    },
  },
  actions: {
    fetchConfig({ commit }) {
      axios.get(backendUrls.config()).then((response) => {
        console.debug('Store got config', response.data)
        commit('updateConfig', response.data)
        commit('updateConfigLoadStatus', loadStatuses.SUCCESS)
      }).catch(err => {
        console.error('Store got error fetching config', err)
        commit('updateConfigLoadStatus', loadStatuses.ERROR)
      })
    },
    fetchSessionUser({ commit }) {
      axios.get(backendUrls.currentUser()).then((response) => {
        console.debug('Store got current user', response.data)
        commit('updateSessionUser', response.data)
        commit('updateSessionUserLoadStatus', loadStatuses.SUCCESS)
      }).catch(err => {
        console.error('Store got error fetching current user', err)
        commit('updateSessionUserLoadStatus', loadStatuses.ERROR)
      })
    },
    async fetchControls({ commit }) {
      const currentURL = window.location.pathname
      if (currentURL === '/faq/' || currentURL === '/declaration-conformite/' || currentURL === '/cgu/' || currentURL.replace(/\d+\/$/, '') === '/questionnaire/corbeille/') {
        // NOTE VUE 3: L'utilisation de 'this.controls' dans l'action est incorrecte en Vuex 4.
        // Vous devez commit la mise à jour après l'appel API.
        let controlsData = [];
        await axios.get(backendUrls.getControlsList()).then(response => {
          controlsData = response.data
        }).catch(err => {
          // Gérer l'erreur si nécessaire
        })
        commit('updateControls', controlsData) // Commit la mise à jour ici
      } else {
        // Si la condition n'est pas remplie, s'assurer que controls n'est pas utilisé sans être initialisé
        commit('updateControls', [])
      }
      commit('updateControlsLoadStatus', loadStatuses.SUCCESS)
    },
  },
})