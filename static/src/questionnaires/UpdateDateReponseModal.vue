<template>
  <div class="modal fade update-date-reponse-modal" id="updateDateReponseModal" tabindex="-1"
       role="dialog" aria-labelledby="labelForModalDateReponse" aria-hidden="true" aria-modal="true">
    <div class="modal-dialog" role="document">
      <div class="modal-content">
        <div class="modal-header">
          <div class="modal-title" id="labelForModalDateReponse">
            {{ questionnaire.title_display }}
          </div>
        </div>
        <div class="modal-body">
          <div v-if="hasErrors" class="alert alert-danger" role="alert">
            La modification de la date de réponse n'a pas fonctionné.
          </div>
          <form @submit.prevent="updateDateReponse" @keydown.esc="resetFormData">
            <div class="form-group">
              <label class="form-label" id="questionnaireEndDate" for="questionnaire_enddate">
                Vous pouvez modifier la date limite de réponse :
              </label>
              <Datepicker id="questionnaire_enddate"
                          class="blue"
                          aria-labelledby="questionnaireEndDate"
                          :language="fr"
                          :typeable="true"
                          :use-utc="true"
                          :placeholder="placeholder"
                          v-model="endDate"
                          :format="format"
                          :monday-first="true" />
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
import { defineComponent, ref, watch, onMounted } from 'vue'
import axios from 'axios'
import Datepicker from 'vue3-datepicker'
import fr from '../utils/vuejs-datepicker-locale-fr'
import backend from '../utils/backend'
import { toBackendFormat } from '../utils/DateFormat'

axios.defaults.xsrfCookieName = 'csrftoken'
axios.defaults.xsrfHeaderName = 'X-CSRFTOKEN'

export default defineComponent({
  name: 'UpdateDateReponseModal',
  props: {
    questionnaireId: { type: Number, required: true },
    questionnaire: { type: Object, required: true },
  },
  emits: ['questionnaire-updated'],
  components: { Datepicker },
  setup(props, { emit }) {
    const endDate = ref(props.questionnaire.end_date || '')
    const hasErrors = ref(false)
    const errors = ref<string[]>([])
    const frLocale = fr
    const format = 'yyyy-MM-dd'
    const placeholder = 'yyyy-mm-dd'

    // Watch prop for changes
    watch(() => props.questionnaire.end_date, (newVal) => {
      endDate.value = newVal
    })

    const resetFormData = () => {
      hasErrors.value = false
      errors.value = []
    }

    const hideThisModal = () => {
      resetFormData()
      const modalEl = document.getElementById('updateDateReponseModal')
      if (modalEl) {
        // Bootstrap 5
        const modalInstance = bootstrap.Modal.getInstance(modalEl)
        modalInstance?.hide()
      }
    }

    const emitQuestionnaireUpdated = () => {
      emit('questionnaire-updated', props.questionnaire)
    }

    const _doSave = async () => {
      const url = backend.questionnaire(props.questionnaire.id)
      props.questionnaire.end_date = toBackendFormat(endDate.value)
      return axios.put(url, props.questionnaire)
    }

    const updateDateReponse = async () => {
      try {
        const response = await _doSave()
        console.debug('Successful response date save.')
        emitQuestionnaireUpdated()
        hideThisModal()
        return response.data
      } catch (error: any) {
        console.error('Error in response date save:', error)
        hasErrors.value = true
        if (error.response && error.response.data) {
          errors.value = Array.isArray(error.response.data) ? error.response.data : [error.response.data]
        } else {
          errors.value = [error.message || 'Erreur inconnue']
        }
      }
    }

    return {
      endDate,
      fr: frLocale,
      format,
      placeholder,
      hasErrors,
      errors,
      resetFormData,
      hideThisModal,
      updateDateReponse,
    }
  },
})
</script>
