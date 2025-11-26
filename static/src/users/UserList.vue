<template>
<div class="card-body" v-if="users && users.length">
  <ul class="list-unstyled list-separated">
    <li class="list-separated-item" v-for="(user, index) in users" :key="user.id || index">
      <div class="flex-row align-items-center">
        <div class="flex-column mr-4">
          <span class="avatar avatar-pink">
            {{ user.first_name.charAt(0) }}{{ user.last_name.charAt(0) }}
          </span>
        </div>
        <div class="flex-column mr-4 flex-grow-1">
          <div>{{ user.first_name }} {{ user.last_name }}</div>
          <small><a :href="'mailto:' + user.email">{{ user.email }}</a></small>
        </div>
        
        <template v-if="accessType === 'demandeur'">
          <button class="fe fe-edit btn btn-outline-primary mr-4"
                  title="Modifier l'utilisateur"
                  aria-label="Modifier l'utilisateur"
                  data-toggle="modal"
                  data-target="#updateUserModal"
                  @click="updateEditingState(user)">
            <span class="sr-only">Modifier l'utilisateur</span>
          </button>
          <button class="fe fe-user-x btn btn-outline-primary mr-4"
                  title="Supprimer l'utilisateur"
                  aria-label="Supprimer l'utilisateur"
                  data-toggle="modal"
                  data-target="#removeUserModal"
                  @click="updateEditingState(user)">
            <span class="sr-only">Supprimer l'utilisateur</span>
          </button>
        </template>
      </div>
    </li>
  </ul>
</div>
</template>

<script lang="ts">
// Suppression de: import { mapFields } from 'vuex-map-fields'
import { mapState } from 'vuex' // Import de mapState de Vuex 4
import { defineComponent } from 'vue'
// Suppression de l'initialisation Vue 2: import Vue from 'vue', import Vuex from 'vuex', Vue.use(Vuex)

// Suppression de l'import du store: import { store } from '../store'

export default defineComponent({ // Remplacement de Vue.extend
  // store, // Retiré car injecté globalement par createApp

  props: {
    users: { type: Array, default: () => ([]) },
    control: { type: Object, default: () => ({}) },
    accessType: { type: String, default: '' },
  },
  computed: {
    // --- Remplacement de mapFields par des propriétés calculées GET/SET ---

    // 1. Gère la lecture/écriture du champ 'editingUser' dans le store
    editingUser: {
      get() {
        return this.$store.state.editingUser
      },
      set(user) {
        // Appelle la mutation 'setEditingUser' (ajoutée dans le store migré)
        this.$store.commit('setEditingUser', user) 
      }
    },

    // 2. Gère la lecture/écriture du champ 'editingControl' dans le store
    editingControl: {
      get() {
        return this.$store.state.editingControl
      },
      set(control) {
        // Appelle la mutation 'setEditingControl' (ajoutée dans le store migré)
        this.$store.commit('setEditingControl', control)
      }
    },

    // 3. Champ en lecture seule : utilisation de mapState
    ...mapState(['sessionUser']),
  },
  methods: {
    updateEditingState(user) {
      // Ces affectations appellent les SETTERS des propriétés calculées ci-dessus.
      // 1. Mise à jour de editingControl
      this.editingControl = this.control 
      
      // 2. Mise à jour de editingUser (création d'une copie propre avant mutation)
      // L'ancienne logique `this.editingUser = {}; Object.assign(this.editingUser, user)` 
      // est remplacée par un envoi d'objet propre à la mutation.
      const userCopy = Object.assign({}, user);
      this.editingUser = userCopy;
    },
  }
})
</script>