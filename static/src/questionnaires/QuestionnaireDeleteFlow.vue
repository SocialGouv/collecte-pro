<template>
  <modal-flow ref="modalFlow" :action-function="callDeleteQuestionnaireAPI">

    <template v-slot:confirm-modal-form>
      <div class="modal-header border-bottom-0">
        <div id="modal_title" class="modal-title">
          <div class="mb-4">Vous êtes sur le point de supprimer :</div>
          <div>Questionnaire {{ questionnaire.numbering }} : {{ questionnaire.title }}</div>
        </div>
      </div>

      <div class="modal-body">
        <label for="checkCompris" class="custom-control custom-checkbox">
          <input type="checkbox"
                 id="checkCompris"
                 class="custom-control-input"
                 required
                 aria-labelledby="checkCompris">
          <span class="custom-control-label">
            J'ai compris que ce questionnaire sera supprimé pour tous les utilisateurs de l'espace de dépôt.
          </span>
        </label>
      </div>

      <div class="modal-footer border-top-0">
        <button type="button" class="btn btn-secondary" data-dismiss="modal" title="Annuler">
          Annuler
        </button>
        <button type="submit" class="btn btn-primary btn-red" title="Supprimer">
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
        <span class="fe fe-check-circle fg-success big-icon" aria-hidden="true"></span>
        <p class="text-center">Le questionnaire a bien été supprimé.</p>
      </div>
      <div class="modal-footer border-top-0 d-flex justify-content-center">
        <button type="button" class="btn btn-primary" data-dismiss="modal">
          Terminer
        </button>
      </div>
    </template>

  </modal-flow>
</template>

<script>
import { defineComponent } from 'vue'
import ModalFlow from '../utils/ModalFlow'

export default defineComponent({
  name: 'DeleteQuestionnaireModal',
  props: {
    questionnaire: { type: Object, required: true },
  },
  components: {
    ModalFlow,
  },
  methods: {
    start() {
      this.$refs.modalFlow.start()
    },
    callDeleteQuestionnaireAPI() {
      // TODO: remplacer par un vrai appel API
      console.debug('API delete called for questionnaire', this.questionnaire.id)
      return Promise.resolve()
    },
  },
})
</script>
