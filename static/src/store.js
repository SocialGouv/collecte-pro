import axios from 'axios'
// Lightweight compatible replacements for vuex-map-fields getters/mutations.
// We avoid relying on the external package which can be incompatible in this
// environment and provide the minimal behaviour used across the codebase:
// - getter `getField` returns a function that reads a nested path from state
// - mutation `updateField` applies { path, value } to nested state

const getField = (state) => (path) => {
  if (!path) return undefined
  return String(path).split(/[.[\]]+/).filter(Boolean).reduce((acc, key) => {
    return acc === undefined || acc === null ? undefined : acc[key]
  }, state)
}

function updateField(state, { path, value }) {
  if (!path) return
  const keys = String(path).split(/[.[\]]+/).filter(Boolean)
  let obj = state
  for (let i = 0; i < keys.length - 1; i++) {
    const k = keys[i]
    if (obj[k] === undefined || obj[k] === null) {
      // create intermediate object
      // if next key looks like an array index, create array
      const nextKey = keys[i + 1]
      obj[k] = /^[0-9]+$/.test(nextKey) ? [] : {}
    }
    obj = obj[k]
  }
  const lastKey = keys[keys.length - 1]
  obj[lastKey] = value
}
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

  getters: {
    getField,
  },

  mutations: {
    updateField,
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
    // Added helpers used by migrated Vue 3 components
    setCurrentQuestionnaire(state, questionnaire) {
      state.currentQuestionnaire = questionnaire
    },
    setCurrentQuestionnaireThemes(state, themes) {
      if (!state.currentQuestionnaire) state.currentQuestionnaire = {}
      state.currentQuestionnaire.themes = themes
    },
    setEditingUserField(state, { field, value }) {
      if (!state.editingUser) state.editingUser = {}
      state.editingUser[field] = value
    },
    setEditingUser(state, user) {
      state.editingUser = user
    },
    setEditingControl(state, control) {
      state.editingControl = control
    },
    // Convenience mutation used by migrated components to update a single field
    // on the currentQuestionnaire object.
    updateCurrentQuestionnaireField(state, { field, value }) {
      if (!state.currentQuestionnaire) state.currentQuestionnaire = {}
      state.currentQuestionnaire[field] = value
    },
  },

  actions: {
    async fetchConfig({ commit }) {
      try {
        const response = await axios.get(backendUrls.config())
        commit('updateConfig', response.data)
        commit('updateConfigLoadStatus', loadStatuses.SUCCESS)
      } catch (err) {
        commit('updateConfigLoadStatus', loadStatuses.ERROR)
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

    async fetchControls({ commit }) {
      try {
        // Prefer server-injected controls if present in the DOM (injected by Django templates)
        if (typeof document !== 'undefined') {
          const controlsDataEl = document.getElementById('controls-data')
          if (controlsDataEl && controlsDataEl.textContent && controlsDataEl.textContent.trim() !== '') {
            try {
              const controls = JSON.parse(controlsDataEl.textContent)
              console.debug('store.fetchControls: found server-injected controls, count=', Array.isArray(controls) ? controls.length : 'not-array')
              commit('updateControls', controls)
              commit('updateControlsLoadStatus', loadStatuses.SUCCESS)
              return
            } catch (e) {
              console.error('store.fetchControls: failed to parse controls-data', e)
              // fall through to API logic
            }
          }
        }

        const currentURL = window.location.pathname
        console.debug('store.fetchControls currentURL=', currentURL)

        if (
          currentURL === '/faq/' ||
          currentURL === '/declaration-conformite/' ||
          currentURL === '/cgu/' ||
          currentURL.replace(/\d+\/$/, '') === '/questionnaire/corbeille/'
        ) {
          const response = await axios.get(backendUrls.getControlsList())
          console.debug('store.fetchControls got controls count=', Array.isArray(response.data) ? response.data.length : 0)
          commit('updateControls', response.data)
        } else {
          // If the page isn't one of the known static pages, try to fetch the controls
          // from the API rather than silently setting an empty array. This ensures
          // pages like /questionnaire/controle-<id>/creer receive the controls
          // when the server didn't inject them into the DOM.
          try {
            console.debug('store.fetchControls: not a special page, fetching controls from API')
            const response = await axios.get(backendUrls.getControlsList())
            console.debug('store.fetchControls: fetched controls, status=', response.status, 'count=', Array.isArray(response.data) ? response.data.length : 0)
            if (response.status === 200) {
              commit('updateControls', response.data)
            } else {
              console.error('store.fetchControls: unexpected status from controls API', response.status)
              commit('updateControls', [])
              commit('updateControlsLoadStatus', loadStatuses.ERROR)
              return
            }
          } catch (err) {
            console.error('store.fetchControls: failed to fetch controls from API', err)
            // Fallback to empty array to avoid leaving controls undefined
            commit('updateControls', [])
            commit('updateControlsLoadStatus', loadStatuses.ERROR)
            return
          }
        }

        commit('updateControlsLoadStatus', loadStatuses.SUCCESS)
      } catch (err) {
        console.error('store.fetchControls error', err)
        commit('updateControlsLoadStatus', loadStatuses.ERROR)
      }
    },
  },
})
