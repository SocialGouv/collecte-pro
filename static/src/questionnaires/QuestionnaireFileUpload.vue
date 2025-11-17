<template>
  <div>
    <error-bar v-if="errorMessage" @dismissed="clearError">
      <p>{{ errorMessage }}</p>
    </error-bar>

    <div v-if="questionnaire.id">
      <label class="btn btn-primary">
        <span class="fe fe-upload mr-2"></span>
        Ajouter une pièce jointe
        <input type="file" ref="fileInput" @change="handleFileUpload" hidden/>
      </label>
    </div>

    <div v-else>
      <label class="btn btn-primary disabled">
        <span class="fe fe-upload mr-2"></span>
        Ajouter une pièce jointe
      </label>
      <div class="small">Pour pouvoir ajouter des pièces jointes,</div>
      <div class="small">vous devez d'abord enregistrer</div>
      <div class="small">votre brouillon.</div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref } from 'vue'
import axios from 'axios'
import backendUrls from '../utils/backend'
import ErrorBar from '../utils/ErrorBar'

export default defineComponent({
  name: 'QuestionnaireFileUpload',
  props: {
    questionnaire: { type: Object, default: () => ({ questionnaire_files: [] }) },
  },
  components: { ErrorBar },
  setup(props) {
    const errorMessage = ref<string | undefined>()
    const fileInput = ref<HTMLInputElement | null>(null)

    const clearError = () => {
      errorMessage.value = undefined
    }

    const handleFileUpload = () => {
      clearError()
      if (!fileInput.value || !fileInput.value.files?.length) return

      const file = fileInput.value.files[0]
      const formData = new FormData()
      formData.append('file', file)
      formData.append('questionnaire', props.questionnaire.id)

      axios.post(backendUrls.piecejointe(), formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
      .then(response => {
        const newFile = response.data
        props.questionnaire.questionnaire_files.push(newFile)
      })
      .catch(error => {
        console.error('Error when posting questionnaire file', error)
        if (error.response && Array.isArray(error.response.data)) {
          errorMessage.value = error.response.data[0]
        } else {
          errorMessage.value = 'La pièce jointe n\'a pu être sauvée.'
        }
      })
    }

    return { errorMessage, fileInput, clearError, handleFileUpload }
  },
})
</script>
