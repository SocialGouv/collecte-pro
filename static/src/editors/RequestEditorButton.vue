<template>
  <div>
    <div class="alert alert-secondary" role="alert">
      <div class="flex-row justify-content-between align-items-center">

        <div>
          <span class="fe fe-users mr-1" aria-hidden="true"></span>

          <div v-if="questionnaire.editor">
            <p>
              <strong>{{ questionnaire.editor.first_name }} {{ questionnaire.editor.last_name }}</strong>
              est actuellement la seule personne qui peut modifier ce questionnaire.
            </p>
          </div>

          <div v-else>
            <p>Personne n'est actuellement affecté à la rédaction de ce questionnaire.</p>
          </div>
        </div>

        <div class="text-right">
          <button
            v-if="questionnaire.editor"
            type="submit"
            class="btn btn-gray obtain-rights-button"
            title="Obtenir les droits de rédaction..."
            data-toggle="modal"
            data-target="#requestEditorModal"
          >
            <span class="fa fa-exchange-alt mr-1" aria-hidden="true"></span>
            <span>Obtenir les droits de rédaction...</span>
          </button>

          <button
            v-else
            type="submit"
            class="btn btn-gray obtain-rights-button"
            title="Obtenir les droits de rédaction..."
            @click="takeEditorRights"
          >
            <span class="fa fa-exchange-alt mr-1" aria-hidden="true"></span>
            <span>Obtenir les droits de rédaction...</span>
          </button>
        </div>

      </div>

      <error-bar v-if="errorMessage.length > 0" class="mt-4">
        <p>{{ errorMessage }}</p>
      </error-bar>
    </div>

    <request-editor-modal
      id="requestEditorModal"
      :questionnaire="questionnaire"
      @request-editor="requestEditor"
    ></request-editor-modal>

    <request-editor-confirm-modal
      id="requestEditorConfirmModal"
      @confirm="takeEditorRights"
    ></request-editor-confirm-modal>

  </div>
</template>

<script>
import { reactive, computed } from 'vue'
import { useStore } from 'vuex'
import axios from 'axios'
import backendUrls from '../utils/backend.js'
import RequestEditorConfirmModal from '../editors/RequestEditorConfirmModal'
import ErrorBar from '../utils/ErrorBar'
import RequestEditorModal from '../editors/RequestEditorModal'

export default {
  props: {
    questionnaire: Object,
    window: {
      default: () => window,
    },
  },
  components: {
    ErrorBar,
    RequestEditorConfirmModal,
    RequestEditorModal,
  },
  setup(props) {
    const store = useStore()
    const state = reactive({
      errorMessage: '',
    })

    // Remplace mapFields('sessionUser')
    const sessionUser = computed(() => store.state.sessionUser)

    const callSwapEditorApi = (editorUser, questionnaireId) => {
      const url = backendUrls.swapEditor(questionnaireId)
      return axios.put(url, { editor: editorUser })
    }

    const takeEditorRights = () => {
      state.errorMessage = ''
      callSwapEditorApi(sessionUser.value.id, props.questionnaire.id)
        .then((response) => {
          props.window.location.assign(
            backendUrls['questionnaire-edit'](props.questionnaire.id)
          )
        })
        .catch(() => {
          state.errorMessage =
            "Erreur lors de l'obtention des droits. Vous pouvez réessayer."
        })
    }

    const requestEditor = () => {
      $('#requestEditorModal').modal('hide')
      $('#requestEditorConfirmModal').modal('show')
    }

    return {
      ...state,
      sessionUser,
      callSwapEditorApi,
      takeEditorRights,
      requestEditor,
    }
  },
}
</script>
