<template>

<div class="modal fade update-user-modal" id="updateUserModal" tabindex="-1" role="dialog" aria-labelledby="labelForModalAddUser" aria-hidden="true" aria-modal="true">
  <div class="modal-dialog" role="document">
    <div class="modal-content">
      <div class="modal-header">
        <div class="modal-title" id="labelForModalAddUser">{{ localEditingControl.title }}</div>
      </div>
      <div class="modal-body">
        <div v-if="hasErrors" class="alert alert-danger" role="alert">
          <div v-if="errorMessages.length > 0">
            <div v-for="(msg, idx) in errorMessages" :key="idx" class="mb-2">
              {{ msg }}
            </div>
          </div>
          <div v-else>La modification d'utilisateur n'a pas fonctionné.</div>
        </div>

          <div class="form-group">
            <p class="form-label">Email : {{ localEditingUser.email}}</p>
            <p class="small text-muted">
              Pour modifier un email, vous devez supprimer l'utilisateur et en créer un nouveau.
            </p>
            <button class="btn btn-secondary btn-sm" @click="showRemoveModal">
              Supprimer l'utilisateur
            </button>
          </div>
        <form @submit.prevent="updateUser" @keydown.esc="resetFormData">
          <div class="form-fieldset">
            <div class="form-group">
              <label id="first-name-label" class="form-label">
                Prénom
                <span class="form-required"></span>
              </label>
              <input type="text"
                    class="form-control"
                    v-bind:class="{ 'state-invalid': errors.first_name }"
                    v-model="localFirstName"
                    required
                    aria-labelledby="first-name-label">
            </div>
            <div class="form-group">
              <label id="last-name-label" class="form-label">
                Nom
                <span class="form-required"></span>
              </label>
              <input type="text"
                    class="form-control"
                    v-bind:class="{ 'state-invalid': errors.last_name }"
                    v-model="localLastName"
                    required
                    aria-labelledby="last-name-label">
            </div>
          </div>
          <div class="text-right">
            <button type="button" class="btn btn-secondary" @click="hideThisModal">Annuler</button>
            <button type="submit" class="btn btn-primary">Modifier</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</div>
</template>

<script lang="ts">
// Suppression de: import { mapFields } from 'vuex-map-fields'
import { mapState } from 'vuex' // mapState pour l'accès en lecture si nécessaire
import { defineComponent } from 'vue'
import axios from 'axios'
import backend from '../utils/backend'
import { validateUserNames } from '../utils/validators'
// Suppression de l'initialisation Vue 2: import Vue from 'vue', import Vuex from 'vuex', Vue.use(Vuex)

// Suppression de: import { store } from '../store'
import EventBus from '../events'

axios.defaults.xsrfCookieName = 'csrftoken'
axios.defaults.xsrfHeaderName = 'X-CSRFTOKEN'

export default defineComponent({ // Remplacement de Vue.extend
  // store, // Retiré

  data: function() {
    return {
      postResult: [],
      errors: [],
      hasErrors: false,
    }
  },
  computed: {
    // expose editingControl and editingUser from store
    ...mapState(['editingControl', 'editingUser']),

    errorMessages(): string[] {
      if (!this.errors || Object.keys(this.errors).length === 0) {
        return [];
      }
      const messages: string[] = [];
      for (const [field, fieldErrors] of Object.entries(this.errors)) {
        if (Array.isArray(fieldErrors) && fieldErrors.length > 0) {
          fieldErrors.forEach(err => {
            messages.push(err);
          });
        }
      }
      return messages;
    },

    localEditingControl() {
      return this.$store.state.editingControl || {}
    },
    localEditingUser() {
      return this.$store.state.editingUser || {}
    },

    // v-model replacements for editingUser fields
    localFirstName: {
      get() {
        return this.$store.state.editingUser?.first_name
      },
      set(value) {
        this.$store.commit('setEditingUserField', { field: 'first_name', value })
      }
    },
    localLastName: {
      get() {
        return this.$store.state.editingUser?.last_name
      },
      set(value) {
        this.$store.commit('setEditingUserField', { field: 'last_name', value })
      }
    },
  },
  methods: {
    showRemoveModal() {
      this.hideThisModal()
      // Assurez-vous que jQuery/Bootstrap est bien chargé dans Vue 3.
      // Le mode compatibilité gère souvent cela, sinon il faudra utiliser une référence Vue 3.
      $('#removeUserModal').modal('show')
    },
    hideThisModal() {
      this.resetFormData()
      $('#updateUserModal').modal('hide')
    },
    resetFormData() {
      this.hasErrors = false
      this.errors = {}
    },
    formatApiErrors(error: any): any {
      const status = error?.response?.status
      const errorData = error?.response?.data
      const knownFieldKeys = ['first_name', 'last_name', 'email', 'non_field_errors', 'profile_type', 'control', 'keycloak_error']

      // Erreur Keycloak structurée : priorité absolue
      if (errorData?.keycloak_error) {
        return { keycloak_error: [errorData.keycloak_error] }
      }

      if (errorData && typeof errorData === 'object' && !Array.isArray(errorData)) {
        const keys = Object.keys(errorData)
        if (keys.length > 0 && keys.some(k => knownFieldKeys.includes(k))) {
          return errorData
        }
      }

      const collectMessages = (value: unknown): string[] => {
        if (!value) return []
        if (typeof value === 'string') return [value]
        if (Array.isArray(value)) return value.flatMap(item => collectMessages(item))
        if (typeof value === 'object') {
          return Object.values(value as Record<string, unknown>).flatMap(item => collectMessages(item))
        }
        return []
      }

      const messages: string[] = []
      if (status) {
        messages.push(`Erreur HTTP ${status}.`)
      }

      const details = collectMessages(errorData)
      details.forEach(msg => messages.push(msg))

      const uniqueMessages = [...new Set(messages)]
      if (uniqueMessages.length > 0) {
        return { error: uniqueMessages }
      }

      return { error: ['Une erreur est survenue. Veuillez reessayer.'] }
    },

    updateUser() {
      this.hasErrors = false
      this.errors = {}

      const validationErrors = validateUserNames(
        this.$store.state.editingUser?.first_name,
        this.$store.state.editingUser?.last_name,
      )
      if (validationErrors.first_name.length > 0 || validationErrors.last_name.length > 0) {
        this.hasErrors = true
        this.errors = validationErrors
        return
      }

      // NOTE: L'objet this.editingUser n'existe plus directement. 
      // Nous utilisons l'état actuel du store (this.$store.state.editingUser)
      const userToUpdate = this.$store.state.editingUser;

      axios.post(backend.user(), userToUpdate)
        .then(response => {
          this.postResult = response.data
          // Utilisation de l'EventBus déprécié, mais conservé pour l'instant.
          EventBus.$emit('users-changed', this.postResult) 
          this.hideThisModal()
        })
        .catch((error) => {
          this.hasErrors = true
          this.errors = this.formatApiErrors(error)
        })
    },
  }
})
</script>