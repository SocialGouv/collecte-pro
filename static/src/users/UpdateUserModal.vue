<template>

<div class="modal fade update-user-modal" id="updateUserModal" tabindex="-1" role="dialog" aria-labelledby="labelForModalAddUser" aria-hidden="true" aria-modal="true">
  <div class="modal-dialog" role="document">
    <div class="modal-content">
      <div class="modal-header">
        <div class="modal-title" id="labelForModalAddUser">{{ localEditingControl.title }}</div>
      </div>
      <div class="modal-body">
        <div v-if="hasErrors" class="alert alert-danger" role="alert">
          La modification d'utilisateur n'a pas fonctionné.
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
              <p class="text-muted pl-2" v-if="errors.first_name">
                <span class="fa fa-warning" aria-hidden="true"></span>
                {{ errors.first_name.join(' / ')}}
              </p>
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
              <p class="text-muted pl-2" v-if="errors.last_name">
                <span class="fa fa-warning" aria-hidden="true"></span>
                {{ errors.last_name.join(' / ')}}
              </p>
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
import axios from 'axios'
import backend from '../utils/backend'
// Suppression de l'initialisation Vue 2: import Vue from 'vue', import Vuex from 'vuex', Vue.use(Vuex)

// Suppression de: import { store } from '../store'
import EventBus from '../events'

axios.defaults.xsrfCookieName = 'csrftoken'
axios.defaults.xsrfHeaderName = 'X-CSRFTOKEN'

export default { // Remplacement de Vue.extend
  // store, // Retiré

  data: function() {
    return {
      postResult: [],
      errors: [],
      hasErrors: false,
    }
  },
  computed: {
    // 1. Remplacement de `editingControl` (lecture seule dans ce contexte)
    localEditingControl: mapState(['editingControl']),

    // 2. Remplacement de `editingUser` (lecture, mais nous le remplaçons par les champs individuels)
    localEditingUser: mapState(['editingUser']),
    
    // 3. Remplacement de v-model="editingUser.first_name"
    localFirstName: {
      get() {
        return this.$store.state.editingUser.first_name
      },
      set(value) {
        // Nouvelle mutation pour mettre à jour un champ spécifique de l'utilisateur
        this.$store.commit('setEditingUserField', { field: 'first_name', value })
      }
    },

    // 4. Remplacement de v-model="editingUser.last_name"
    localLastName: {
      get() {
        return this.$store.state.editingUser.last_name
      },
      set(value) {
        // Nouvelle mutation pour mettre à jour un champ spécifique de l'utilisateur
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
      this.errors = []
    },
    updateUser() {
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
          this.errors = error.response.data
        })
    },
  },
}
</script>