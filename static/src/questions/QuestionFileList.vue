<template>
  <div>
    <error-bar v-if="errorMessage" @dismissed="clearError">
      <p>{{ errorMessage }}</p>
    </error-bar>
    <div v-if="files && files.length" class="question-box-child">
      <div v-if="files.length > 1" class="form-label">Fichiers annexes à la question :</div>
      <div v-else class="form-label">Fichier annexe à la question :</div>
      <ul>
        <li v-for="(file, index) in files" :key="index" class="question-file">
          <a :href="file.url">{{ file.basename }}</a>
          <span v-if="withDelete">
            <button @click.prevent="deleteFile(file.id)"
                    class="btn btn-link"
                    title="Supprimer le fichier">
              <span class="fe fe-trash-2" aria-hidden="true"></span>
              <span class="sr-only">Supprimer le fichier</span>
            </button>
          </span>
        </li>
      </ul>
    </div>
  </div>
</template>

<script>
import { defineComponent, ref } from 'vue'
import axios from 'axios'
import backendUrls from '../utils/backend'
import ErrorBar from '../utils/ErrorBar'

export default defineComponent({
  name: 'QuestionFileList',
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
  components: { ErrorBar },
  setup(props) {
    const errorMessage = ref(undefined)

    const clearError = () => {
      errorMessage.value = undefined
    }

    const deleteFileFromVuex = (fileId) => {
      const index = props.files.findIndex(f => f.id === fileId)
      if (index !== -1) {
        props.files.splice(index, 1)
      }
    }

    const deleteFile = (fileId) => {
      clearError()
      axios.delete(backendUrls.annexe(fileId))
        .then(() => {
          deleteFileFromVuex(fileId)
        })
        .catch((error) => {
          console.error('Error when deleting question file', error)
          errorMessage.value = 'Le fichier n\'a pu être supprimé.'
        })
    }

    return {
      errorMessage,
      clearError,
      deleteFile
    }
  }
})
</script>
