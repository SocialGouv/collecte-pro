<template>
  <div>
    <ErrorBar v-if="errorMessage" @dismissed="clearError">
      <p>{{ errorMessage }}</p>
    </ErrorBar>

    <div v-if="files && files.length" class="question-box-child">
      <div v-if="files.length > 1" class="form-label">Pièces jointes au questionnaire :</div>
      <div v-else class="form-label">Pièce jointe au questionnaire :</div>
      <ul>
        <li v-for="(file, index) in files" :key="index" class="questionnaire-file">
          <a :href="file.url">{{ file.basename }}</a>
          <span v-if="withDelete">
            <button @click.prevent="deleteFile(file.id)" class="btn btn-link" title="Supprimer la pièce jointe">
              <span class="fe fe-trash-2" aria-hidden="true"></span>
              <span class="sr-only">Supprimer la pièce jointe</span>
            </button>
          </span>
        </li>
      </ul>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, toRefs } from 'vue'
import axios from 'axios'
import backendUrls from '../utils/backend'
import ErrorBar from '../utils/ErrorBar'

export default defineComponent({
  name: 'QuestionnaireFileList',
  components: { ErrorBar },
  props: {
    files: {
      type: Array,
      required: true
    },
    withDelete: {
      type: Boolean,
      default: false
    }
  },
  setup(props) {
    const { files, withDelete } = toRefs(props)
    const errorMessage = ref<string | undefined>(undefined)

    const clearError = () => {
      errorMessage.value = undefined
    }

    const deleteFileFromVuex = (fileId: number) => {
      const index = files.value.findIndex(f => f.id === fileId)
      if (index !== -1) {
        files.value.splice(index, 1)
        console.debug('Deleted file', fileId, 'from vuex')
      }
    }

    const deleteFile = (fileId: number) => {
      clearError()
      axios.delete(backendUrls.piecejointe(fileId))
        .then(() => deleteFileFromVuex(fileId))
        .catch((error) => {
          console.error('Error when deleting question file', error)
          errorMessage.value = 'Le fichier n\'a pu être supprimé.'
        })
    }

    return {
      files,
      withDelete,
      errorMessage,
      clearError,
      deleteFile
    }
  }
})
</script>
