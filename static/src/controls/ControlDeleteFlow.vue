<template>
  <modal-flow ref="modalFlow" :action-function="callDeleteControlAPI">

    <template v-slot:confirm-modal-form>
      <div class="modal-header border-bottom-0">
        <div id="modal_title" class="modal-title">
          Vous êtes sur le point de supprimer l'espace de dépôt "{{ control.reference_code }}"
        </div>
      </div>

      <div class="modal-body">
        <fieldset class="form-fieldset">
          <legend>Merci de cocher toutes les cases pour valider cette action</legend>
          <label for="checkbox_1" class="custom-control custom-checkbox">
            <input type="checkbox"
                   id="checkbox_1"
                    class="custom-control-input"
                    required>
            <span class="custom-control-label">Les données ne seront pas récupérables.</span>
          </label>
          <label for="checkbox_2" class="custom-control custom-checkbox">
            <input type="checkbox"
                   id="checkbox_2"
                    class="custom-control-input"
                    required>
            <span class="custom-control-label">
              Tous les utilisateurs de cet espace n'y auront plus accès.
            </span>
          </label>
          <label for="checkbox_3" class="custom-control custom-checkbox">
            <input type="checkbox"
                   id="checkbox_3"
                    class="custom-control-input"
                    required>
            <span class="custom-control-label">
              Je confirme que la suppression des données n'impacte pas la suite
              de la procédure, en cas de contentieux notamment.
            </span>
          </label>
        </fieldset>
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
                title="Supprimer l'espace de dépôt"
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
          L'espace de dépôt <strong>"{{ control.title }}"</strong> a bien été supprimé.
        </p>
      </div>
      <div class="modal-footer border-top-0 d-flex justify-content-center">
        <button type="button"
                class="btn btn-primary"
                @click="goHome"
        >
          <span class="fa fa-chevron-left mr-2" aria-hidden="true"></span>
          Revenir à l'accueil
        </button>
      </div>
    </template>

  </modal-flow>
</template>

<script>
import axios from 'axios'
import backendUrls from '../utils/backend.js'
import ModalFlow from '../utils/ModalFlow'
import Vue from 'vue'

export default Vue.extend({
  props: {
    control: Object,
  },
  components: {
    ModalFlow,
  },
  methods: {
    start() {
      console.debug('outer start!')
      this.$refs.modalFlow.start()
    },
    goHome() {
      window.location.assign('/accueil')
    },
    callDeleteControlAPI() {
      const url = backendUrls.deleteControl(this.control.id)
      return axios.post(url)
    },
  },
})
</script>
