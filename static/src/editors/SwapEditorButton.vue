<template>
  <div>
    <div class="alert alert-info flex-row justify-content-between" role="alert">
      <div class="mt-2">
        <span class="fe fe-users mr-1" aria-hidden="true"></span>
        <strong>Vous</strong> êtes actuellement le rédacteur de ce questionnaire.
      </div>
      <div class="text-right">
        <button type="submit"
                class="btn btn-primary"
                title="Transférer les droits de rédaction..."
                @click="saveDraft">
          <span class="fa fa-exchange-alt mr-1" aria-hidden="true"></span>
          Transférer les droits de rédaction...
        </button>
      </div>
    </div>

    <swap-editor-modal id="swapEditorModal"
                       ref="swapEditorModal"
                       :control-id="controlId"
                       :questionnaire-id="questionnaireId"
                       @swap-editor="swapEditor"
                       @unset-editor="unsetEditor">
    </swap-editor-modal>
    <swap-editor-success-modal id="swapEditorSuccessModal"
                               :questionnaire-id="questionnaireId">
      <h4 class="mb-6">
        Les droits de rédaction ont été transférés à <br>
        {{ newEditor.first_name }} {{ newEditor.last_name }} !
      </h4>
      <p>
        Pour devenir rédacteur de ce questionnaire à nouveau, il faudra que
        votre collègue vous transfère ou libère les droits de rédaction.
      </p>
    </swap-editor-success-modal>
    <swap-editor-success-modal id="unsetEditorSuccessModal"
                               :questionnaire-id="questionnaireId">
      <h4 class="mb-6">
        Les droits de rédaction ont été libérés pour toute l'équipe !
      </h4>
      <p>
        Chaque membre de l'équipe peut maintenant prendre les droits pour devenir rédacteur.
      </p>
    </swap-editor-success-modal>

  </div>
</template>

<script>
import { defineComponent, ref, onMounted } from 'vue'
import axios from 'axios'
import backendUrls from '../utils/backend.js'
import SwapEditorModal from './SwapEditorModal'
import SwapEditorSuccessModal from './SwapEditorSuccessModal'

export default defineComponent({
  name: 'SwapEditorButton',
  props: {
    controlId: Number,
  },
  components: {
    SwapEditorModal,
    SwapEditorSuccessModal,
  },
  setup(props, { emit, expose }) {
    const questionnaireId = ref(undefined)
    const newEditor = ref({})
    const swapEditorModalRef = ref(null)

    const saveDraft = () => {
      emit('save-draft')
    }

    const callSwapEditorApi = (editorUser, questionnaireIdValue) => {
      const url = backendUrls.swapEditor(questionnaireIdValue)
      return axios.put(url, { editor: editorUser })
    }

    const swapEditor = (user) => {
      callSwapEditorApi(user.id, questionnaireId.value)
        .then(() => {
          $('#swapEditorModal').modal('hide')
          newEditor.value = user
          $('#swapEditorSuccessModal').modal('show')
        })
        .catch((error) => {
          swapEditorModalRef.value.showError(
            "Le transfert de droits n'a pas fonctionné. Vous pouvez réessayer. " + error
          )
        })
    }

    const unsetEditor = () => {
      callSwapEditorApi(null, questionnaireId.value)
        .then(() => {
          $('#swapEditorModal').modal('hide')
          $('#unsetEditorSuccessModal').modal('show')
        })
        .catch((error) => {
          swapEditorModalRef.value.showError(
            "Le transfert de droits n'a pas fonctionné. Vous pouvez réessayer. " + error
          )
        })
    }

    onMounted(() => {
      const showModal = (id) => {
        questionnaireId.value = id
        $('#swapEditorModal').modal('show')
      }
      // Lien avec l'événement parent
      // Assure-toi que ton parent émet 'show-swap-editor-modal'
      if (typeof window !== 'undefined') {
        window.$parent?.$on('show-swap-editor-modal', showModal)
      }
    })

    return {
      questionnaireId,
      newEditor,
      swapEditorModalRef,
      saveDraft,
      swapEditor,
      unsetEditor,
    }
  },
})
</script>
