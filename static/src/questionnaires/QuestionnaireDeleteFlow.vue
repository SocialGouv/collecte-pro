<template>
  <modal-flow ref="modalFlow" :action-function="callDeleteQuestionnaireAPI">

    <template v-slot:confirm-modal-form>
      <div class="modal-header border-bottom-0">
        <div id="modal_title" class="modal-title">
          <div class="mb-4">
            Vous êtes sur le point de supprimer :
          </div>
          <div>
            Questionnaire {{ questionnaire.numbering }} : {{ questionnaire.title }}
          </div>
        </div>
      </div>

      <div class="modal-body">
        <label for="checkCompris" class="custom-control custom-checkbox">
          <input type="checkbox"
                  id="checkCompris"
                  class="custom-control-input"
                  required>
          <span class="custom-control-label">
            J'ai compris que ce questionnaire sera supprimé pour tous les utilisateurs de l'espace
            de dépôt.
          </span>
        </label>
      </div>

      <div class="modal-footer border-top-0">
        <button type="button"
                class="btn btn-secondary"
                data-dismiss="modal"
                title="Annuler"
        >
          Annuler
        </button>
        <button type="submit"
                class="btn btn-primary btn-red"
                title="Forcer le transfert"
        >
          <span class="fe fe-trash-2 mr-1" aria-hidden="true"></span>
          Supprimer
        </button>
      </div>
    </template>

    <template v-slot:wait-message>
      Suppression en cours...
    </template>

    <template v-slot:success-modal-body>
      <div class="modal-header border-bottom-0 flex-column align-items-center">
        <p>
          <span class="fe fe-check-circle fg-success big-icon" aria-hidden="true"></span>
        </p>
        <p id="modal_title" class="text-center">
          Le questionnaire a bien été supprimé.
        </p>
      </div>
      <div class="modal-footer border-top-0 d-flex justify-content-center">
        <button type="button"
                class="btn btn-primary"
                data-dismiss="modal"
        >
          Terminer
        </button>
      </div>
    </template>

  </modal-flow>
</template>

<script>
import ModalFlow from '../utils/ModalFlow'
import Vue from 'vue'

export default Vue.extend({
  props: {
    questionnaire: Object,
  },
  components: {
    ModalFlow,
  },
  methods: {
    start() {
      console.debug('outer start!')
      this.$refs.modalFlow.start()
    },
    callDeleteQuestionnaireAPI() {
      // Todo call real API
      console.log('calling API...')
      return Promise.resolve()
    },
  },
})
</script>
