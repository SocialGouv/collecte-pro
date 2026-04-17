<template>
    <div class="modal fade update-date-reponse-modal" id="updateDateReponseModal" tabindex="-1"
        role="dialog" aria-labelledby="labelForModalDateReponse" aria-hidden="true"
        aria-modal="true">
      <div class="modal-dialog" role="document">
        <div class="modal-content">
          <div class="modal-header">
            <div class="modal-title" id="labelForModalDateReponse">
                {{questionnaire.title_display}}
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
                    <datepicker id="questionnaire_enddate"
                                class="blue"
                                aria-labelledby="questionnaireEndDate"
                                :locale="fr"
                                :typeable="true"
                                :use-utc="true"
                                :placeholder="placeholder"
                                :model-value="endDate"
                                @update:model-value="endDate = $event"
                                :format="format"
                                :monday-first="true">
                    </datepicker>
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
import { defineComponent, ref } from 'vue'
import axios from 'axios'
import Datepicker from 'vue3-datepicker'
import { fr } from 'date-fns/locale'
import backend from '../utils/backend'
import { toBackendFormat } from '../utils/DateFormat'


declare const $: any

axios.defaults.xsrfCookieName = 'csrftoken'
axios.defaults.xsrfHeaderName = 'X-CSRFTOKEN'

export default defineComponent({
  name: 'UpdateDateReponseModal',
  props: {
    questionnaireId: Number,
    questionnaire: Object as any,
  },
  components: {
    Datepicker,
  },
  setup(props, { emit }) {
    const endDate = ref<Date | null>(null)
    const postResult = ref([])
    const errors = ref<any[]>([])
    const hasErrors = ref(false)
    const format = 'yyyy-MM-dd'
    const placeholder = 'yyyy-mm-dd'

    // Initialize endDate from questionnaire (same as created() hook in Vue 2)
    if (props.questionnaire?.end_date) {
      endDate.value = new Date(props.questionnaire.end_date as string)
    }

    const hideThisModal = () => {
      resetFormData()
      $('#updateDateReponseModal').modal('hide')
    }

    const resetFormData = () => {
      hasErrors.value = false
      errors.value = []
    }

    const emitQuestionnaireUpdated = () => {
      emit('questionnaire-updated', props.questionnaire)
    }

    const _doSave = async () => {
      // Create a copy to avoid mutating the prop
      const questionnaireCopy = { ...props.questionnaire }
      questionnaireCopy.end_date = toBackendFormat(endDate.value)
      const url = backend.questionnaire(questionnaireCopy.id)
      return axios.put(url, questionnaireCopy)
    }

    const updateDateReponse = async () => {
      try {
        const response = await _doSave()
        postResult.value = response.data
        emitQuestionnaireUpdated()
        hideThisModal()
        return response.data
      } catch (error: any) {
        console.error('Error in response date save:', error)
        hasErrors.value = true
        const errorToDisplay = (error.response && error.response.data) ? error.response.data : error
        if (Array.isArray(errorToDisplay)) {
          errors.value = errorToDisplay
        } else if (typeof errorToDisplay === 'string') {
          errors.value = [errorToDisplay]
        } else {
          errors.value = [error.message || 'Erreur inconnue']
        }
      }
    }

    return {
      endDate,
      fr,
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