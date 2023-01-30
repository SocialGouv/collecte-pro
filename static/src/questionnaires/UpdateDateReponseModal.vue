<template>
    <div class="modal fade update-date-reponse-modal" id="updateDateReponseModal" tabindex="-1" 
        role="dialog" aria-labelledby="labelForModalDateReponse" aria-hidden="true" 
        aria-modal="true">
      <div class="modal-dialog" role="document">
        <div class="modal-content">
          <div class="modal-header">
            <div class="modal-title" id="labelForModalDateReponse">Coucou la modif</div>
          </div>
          <div class="modal-body">
            <div v-if="hasErrors" class="alert alert-danger" role="alert">
              La modification de la date de réponse n'a pas fonctionné.
            </div>
            <form @submit.prevent="updateDateReponse" @keydown.esc="resetFormData">
                <div class="form-group">
                    <label class="form-label" id="questionnaireEndDate" for="questionnaire_enddate">
                    Vous pouvez indiquer la date limite de réponse :
                    </label>
                    <datepicker id="questionnaire_enddate"
                                class="blue"
                                aria-labelledby="questionnaireEndDate"
                                :language="fr"
                                :typeable="true"
                                :placeholder="placeholder"
                                :v-model="questionnaire.end_date"
                                :format="format"
                                :monday-first="true">
                    </datepicker>
                </div>
                <div class="text-right">
                    <button type="button" class="btn btn-secondary" @click="hideThisModal"
                        >Annuler
                    </button>
                    <button type="submit" class="btn btn-primary">Modifier</button>
                </div>
            </form>
          </div>
        </div>
      </div>
    </div>
</template>

<script>
import axios from 'axios'
import Vue from 'vue'

import { store } from '../store'
import Datepicker from 'vuejs-datepicker'
import fr from '../utils/vuejs-datepicker-locale-fr'
import backend from '../utils/backend'

axios.defaults.xsrfCookieName = 'csrftoken'
axios.defaults.xsrfHeaderName = 'X-CSRFTOKEN'

export default Vue.extend({
  store,
  props: {
    questionnaireId: Number,
    questionnaire: Object,
  },
  components: {
    Datepicker,
  },
  data() {
    return {
      fr: fr, // locale for datepicker
      format: 'yyyy-MM-dd', // format for datepicker
      placeholder: 'yyyy-mm-dd', // Placeholder for datepicker
      postResult: [],
      errors: [],
      hasErrors: false,
    }
  },
  methods: {
    showRemoveModal() {
      this.hideThisModal()
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
    updateDateReponse() {
      console.log('on va update la date echeance')
      console.log('notre questionnaire : ', this.questionnaireId)
      axios.put.bind(this, backend.questionnaire(this.questionnaireId))
        .then(response => {
          this.postResult = response.data
          this.hideThisModal()
        })
        .catch((error) => {
          this.hasErrors = true
          this.errors = error.response.data
        })
    },
  },
})
</script>

<style></style>
