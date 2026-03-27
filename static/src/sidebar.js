// static/src/sidebar.js
// Remplacement de @babel/polyfill
import 'core-js/stable'
import 'regenerator-runtime/runtime'
import './utils/polyfills.js'          // Polyfills éventuels pour le navigateur
import { createApp, h } from 'vue'       // Vue 3
import { store, loadStatuses } from './store'       // Store Vuex
import Sidebar from './utils/Sidebar.vue' // Composant Sidebar

// Création de l'application Vue 3
const app = createApp({
  render: () => h(Sidebar),
  mounted() {
    // Si le template Django a injecté des données 'controls-data' dans le DOM,
    // les utiliser pour initialiser le store au lieu d'appeler l'API.
    const controlsDataEl = document.getElementById('controls-data')
    if (controlsDataEl) {
      try {
        const controls = JSON.parse(controlsDataEl.textContent)
        this.$store.commit('updateControls', controls)
        this.$store.commit('updateControlsLoadStatus', loadStatuses.SUCCESS)

        // If the server also injected the session user, use it, otherwise
        // dispatch a fetch for it so `isLoaded` becomes true.
        const userDataEl = document.getElementById('user-data')
        if (userDataEl) {
          try {
            const user = JSON.parse(userDataEl.textContent)
            this.$store.commit('updateSessionUser', user)
            this.$store.commit('updateSessionUserLoadStatus', loadStatuses.SUCCESS)
          } catch (e) {
            console.error('Sidebar: impossible de parser user-data', e)
            this.$store.dispatch('fetchSessionUser')
          }
        } else {
          this.$store.dispatch('fetchSessionUser')
        }

        // Always fetch config (not always injected server-side)
        this.$store.dispatch('fetchConfig')
      } catch (e) {
        console.error('Sidebar: impossible de parser controls-data', e)
        // fallback to fetching from API
        this.$store.dispatch('fetchSessionUser')
        this.$store.dispatch('fetchControls')
        this.$store.dispatch('fetchConfig')
      }
    } else {
      // Actions de chargement initial
      this.$store.dispatch('fetchSessionUser')
      this.$store.dispatch('fetchControls')
      this.$store.dispatch('fetchConfig')
    }
  },
})

// Utilisation du store Vuex
app.use(store)

// Montage sur l'élément HTML
const sidebarEl = document.getElementById('sidebar-vm')
if (sidebarEl) {
  app.mount('#sidebar-vm')
} else {
  console.error('Sidebar: #sidebar-vm element not found in DOM!')
}

