import axios from 'axios'
import backendUrls from './utils/backend.js'
import { createStore } from 'vuex'

export const loadStatuses = {
  LOADING: Symbol('LOADING'),
  SUCCESS: Symbol('SUCCESS'),
  ERROR: Symbol('ERROR'),
}

export const store = createStore({
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

  mutations: {
    updateControls(state, controls) {
      state.controls = controls
    },
    updateControlsLoadStatus(state, status) {
      state.controlsLoadStatus = status
    },
    updateSessionUser(state, user) {
      state.sessionUser = user
    },
    updateSessionUserLoadStatus(state, status) {
      state.sessionUserLoadStatus = status
    },
    updateConfig(state, config) {
      state.config = config
    },
    updateConfigLoadStatus(state, status) {
      state.configLoadStatus = status
    },
  },

  actions: {
    async fetchControls({ state, commit }) {
      // Skip fetch si les controls sont déjà présents
      if (state.controls.length > 0 && state.controlsLoadStatus === loadStatuses.SUCCESS) {
        console.debug('store.fetchControls: controls already loaded, skipping fetch')
        return
      }

      // Prefer server-injected controls si présents
      if (typeof document !== 'undefined') {
        const controlsDataEl = document.getElementById('controls-data')
        if (controlsDataEl && controlsDataEl.textContent.trim() !== '') {
          try {
            const controls = JSON.parse(controlsDataEl.textContent)
            console.debug('store.fetchControls: loaded server-injected controls, count=', controls.length)
            commit('updateControls', controls)
            commit('updateControlsLoadStatus', loadStatuses.SUCCESS)
            return
          } catch (e) {
            console.error('store.fetchControls: failed to parse controls-data', e)
          }
        }
      }

      // Fallback API
      try {
        commit('updateControlsLoadStatus', loadStatuses.LOADING)
        const response = await axios.get(backendUrls.getControlsList())
        commit('updateControls', response.data)
        commit('updateControlsLoadStatus', loadStatuses.SUCCESS)
      } catch (err) {
        console.error('store.fetchControls: failed to fetch controls', err)
        commit('updateControls', [])
        commit('updateControlsLoadStatus', loadStatuses.ERROR)
      }
    },

    async fetchSessionUser({ commit }) {
      try {
        const response = await axios.get(backendUrls.currentUser())
        commit('updateSessionUser', response.data)
        commit('updateSessionUserLoadStatus', loadStatuses.SUCCESS)
      } catch (err) {
        commit('updateSessionUserLoadStatus', loadStatuses.ERROR)
      }
    },

    async fetchConfig({ commit }) {
      try {
        const response = await axios.get(backendUrls.config())
        commit('updateConfig', response.data)
        commit('updateConfigLoadStatus', loadStatuses.SUCCESS)
      } catch (err) {
        commit('updateConfigLoadStatus', loadStatuses.ERROR)
      }
    },
  },
})
