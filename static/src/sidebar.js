// static/src/sidebar.js
// Remplacement de @babel/polyfill
import 'core-js/stable'
import 'regenerator-runtime/runtime'
import './utils/polyfills.js'          // Polyfills éventuels pour le navigateur
import { createApp } from 'vue'       // Vue 3
import { store } from './store'       // Store Vuex
import Sidebar from './utils/Sidebar.vue' // Composant Sidebar

// Création de l'application Vue 3
const app = createApp({
  components: { Sidebar },
  mounted() {
    // Actions de chargement initial
    this.$store.dispatch('fetchSessionUser')
    console.log('fetch controls .....')
    this.$store.dispatch('fetchControls')
    this.$store.dispatch('fetchConfig')
  },
})

// Utilisation du store Vuex
app.use(store)

// Montage sur l'élément HTML
app.mount('#sidebar-vm')
