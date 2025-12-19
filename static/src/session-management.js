// Remplacement de @babel/polyfill
import 'core-js/stable'
import 'regenerator-runtime/runtime'
import './utils/polyfills.js'
import { createApp } from 'vue'
import SessionTimeout from './session/SessionTimeout.vue'

const app = createApp({
  components: { SessionTimeout },
})

app.mount('#session-management-vm')
