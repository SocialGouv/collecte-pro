<template>
<div class="modal fade remove-user-modal"
     id="removeUserModal"
     tabindex="-1"
     role="dialog"
     aria-labelledby="removeUserModal"
     aria-hidden="true"
     aria-modal="true">
  <div class="modal-dialog modal-sm modal-notify modal-danger" role="document">
    <div class="modal-content text-center">
      <div class="modal-body">
        <div class="alert alert-warning" role="alert">
          <div>Confirmer la suppression</div>
          <error-bar v-if="hasErrors" :noclose="true">
            <p>La suppression d'utilisateur n'a pas fonctionné.</p>
          </error-bar>
          <p>
            {{ editingUser.first_name }} {{ editingUser.last_name }}
            n'aura plus accès à cette procédure :
            {{ editingControl.title }}.
          </p>
          <div class="btn-list">
            <button @click="remove()" class="btn btn-danger" type="submit">
              Supprimer
            </button>
            <button @click="cancel()" class="btn btn-secondary" type="button" data-dismiss="modal">
              Annuler
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</div>
</template>

<script lang="ts">
import axios from 'axios'
// Suppression de: import { mapFields } from 'vuex-map-fields'
import { mapState } from 'vuex' // Import de mapState de Vuex 4
import backend from '../utils/backend'
// Suppression de l'import de Vue 2 et du store injecté localement

import ErrorBar from '../utils/ErrorBar'
import EventBus from '../events'

export default { // Remplacement de Vue.extend
  // store, // Retiré
  data: function() {
    return {
      postResult: {},
      hasErrors: false,
      error: undefined,
    }
  },
  components: {
    ErrorBar,
  },
  computed: {
    // Remplacement de mapFields par mapState (Lecture seule)
    ...mapState([
      'editingUser',
      'editingControl',
    ]),
  },
  methods: {
    cancel() {
      this.hasErrors = false
      this.error = undefined
    },
    remove() {
      this.hasErrors = false
      this.error = undefined

      var postData = { control: this.editingControl.id }
      // NOTE: Le code utilise les champs du store (editingUser.id, editingControl.id)
      axios.post(backend.removeUserFromControl(this.editingUser.id), postData)
        .then(response => {
          this.postResult = response.data
          // Utilisation de l'EventBus global (conservé pour l'instant)
          EventBus.$emit('users-changed', this.postResult) 
          // Assurez-vous que jQuery/Bootstrap est disponible
          $('#removeUserModal').modal('hide')
        })
        .catch(error => {
          this.hasErrors = true
          this.error = error
        })
    },
  },
}
</script>