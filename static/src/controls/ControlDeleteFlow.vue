<template>
  <ModalFlow ref="modalFlow" :action-function="callDeleteControlAPI">

    <!-- Formulaire de confirmation -->
    <template #confirm-modal-form>
      <div class="modal-header border-bottom-0">
        <div id="modal_title" class="modal-title">
          Vous êtes sur le point de supprimer l'espace de dépôt "{{ control.reference_code }}"
        </div>
      </div>

      <div class="modal-body">
        <fieldset class="form-fieldset">
          <legend>Merci de cocher toutes les cases pour valider cette action</legend>

          <label for="checkbox_1" class="custom-control custom-checkbox">
            <input type="checkbox" id="checkbox_1" v-model="checkbox1" class="custom-control-input" required>
            <span class="custom-control-label">Les données ne seront pas récupérables.</span>
          </label>

          <label for="checkbox_2" class="custom-control custom-checkbox">
            <input type="checkbox" id="checkbox_2" v-model="checkbox2" class="custom-control-input" required>
            <span class="custom-control-label">Tous les utilisateurs de cet espace n'y auront plus accès.</span>
          </label>

          <label for="checkbox_3" class="custom-control custom-checkbox">
            <input type="checkbox" id="checkbox_3" v-model="checkbox3" class="custom-control-input" required>
            <span class="custom-control-label">
              Je confirme que la suppression des données n'impacte pas la suite de la procédure.
            </span>
          </label>
        </fieldset>
      </div>

      <div class="modal-footer border-top-0">
        <button type="button" class="btn btn-secondary" @click="cancelAction">Annuler</button>
        <button type="submit" class="btn btn-primary btn-red" :disabled="!allChecked">
          <span class="fe fe-trash-2 mr-1" aria-hidden="true"></span>
          Supprimer
        </button>
      </div>
    </template>

    <!-- Message d'attente -->
    <template #wait-message>
      Suppression en cours...
    </template>

    <!-- Message de succès -->
    <template #success-modal-body>
      <div class="modal-header border-bottom-0 flex-column align-items-center">
        <p>
          <span class="fe fe-check-circle fg-success big-icon" aria-hidden="true"></span>
        </p>
        <p id="modal_title" class="text-center">
          L'espace de dépôt <strong>"{{ control.title }}"</strong> a bien été supprimé.
        </p>
      </div>
      <div class="modal-footer border-top-0 d-flex justify-content-center">
        <button type="button" class="btn btn-primary" @click="goHome">
          <span class="fa fa-chevron-left mr-2" aria-hidden="true"></span>
          Revenir à l'accueil
        </button>
      </div>
    </template>

    <!-- Message d'erreur -->
    <template #error-modal-body>
      <div class="modal-header border-bottom-0 flex-column align-items-center">
        <p>
          <span class="fe fe-alert-triangle fg-danger big-icon" aria-hidden="true"></span>
        </p>
        <p id="modal_title" class="text-center">
          Une erreur est survenue lors de la suppression de l'espace de dépôt.
        </p>
        <p class="text-center text-danger">{{ errorMessage }}</p>
      </div>
      <div class="modal-footer border-top-0 d-flex justify-content-center">
        <button type="button" class="btn btn-secondary" @click="cancelAction">
          Fermer
        </button>
      </div>
    </template>

  </ModalFlow>
</template>

<script setup>
import { ref, computed } from 'vue'
import axios from 'axios'
import backendUrls from '../utils/backend.js'
import ModalFlow from '../utils/ModalFlow'

const props = defineProps({
  control: Object
})

const modalFlow = ref(null)
const errorMessage = ref('')

// Checkboxes
const checkbox1 = ref(false)
const checkbox2 = ref(false)
const checkbox3 = ref(false)

// Validation : toutes les cases cochées
const allChecked = computed(() => checkbox1.value && checkbox2.value && checkbox3.value)

// Méthodes
const goHome = () => {
  window.location.assign('/accueil')
}

const cancelAction = () => {
  modalFlow.value?.reset()
}

// Appel API pour supprimer le contrôle
const callDeleteControlAPI = async () => {
  try {
    const url = backendUrls.deleteControl(props.control.id)
    const response = await axios.post(url)
    return response
  } catch (error) {
    errorMessage.value = error.response?.data || error.message || 'Erreur inconnue'
    throw error
  }
}

// Fonction pour démarrer le modal depuis l'extérieur
const start = () => {
  modalFlow.value?.start()
}
</script>
