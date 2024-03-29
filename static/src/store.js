import axios from 'axios'
import { getField, updateField } from 'vuex-map-fields'
import backendUrls from './utils/backend.js'
import Vue from 'vue'
import Vuex from 'vuex'

Vue.use(Vuex)

export const loadStatuses = {
  LOADING: Symbol('LOADING'),
  SUCCESS: Symbol('SUCCESS'),
  ERROR: Symbol('ERROR'),
}

export const store = new Vuex.Store({
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
        await axios.get(backendUrls.getControlsList()).then(response => {
          this.controls = response.data
        }).catch(err => {
        })
      }
      commit('updateControls', this.controls)
      commit('updateControlsLoadStatus', loadStatuses.SUCCESS)
    },
  },
})
