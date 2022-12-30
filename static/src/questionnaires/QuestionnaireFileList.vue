<template>
  <div>
    <error-bar v-if="errorMessage" @dismissed="clearError">
      <p>{{ errorMessage }}</p>
    </error-bar>
    <div v-if="files && files.length" class="question-box-child">
      <div v-if="files.length > 1" class="form-label">Pièces jointes au questionnaire :</div>
      <div v-else class="form-label">Pièce jointe au questionnaire :</div>
      <ul>
        <li v-for="(file, index) in files"
            :key="index"
            class="questionnaire-file">
          <a :href="file.url">
            {{ file.basename }}
          </a>
          <span v-if="withDelete">
            <button @click.prevent="deleteFile(file.id)"
                    class="btn btn-link"
                    title="Supprimer la pièce jointe">
              <span class="fe fe-trash-2" aria-hidden="true"></span>
              <span class="sr-only">Supprimer la pièce jointe</span>
            </button>
          </span>
        </li>
      </ul>
    </div>
  </div>
</template>

<script>
import axios from 'axios'
import backendUrls from '../utils/backend'
import ErrorBar from '../utils/ErrorBar'
import Vue from 'vue'

export default Vue.extend({
  props: {
    files: Array,
    withDelete: {
      type: Boolean,
      default: false,
    },
  },
  data() {
    return {
      errorMessage: undefined,
    }
  },
  components: {
    ErrorBar,
  },
  methods: {
    clearError() {
      this.errorMessage = undefined
    },
    deleteFileFromVuex(fileId) {
      for (let i = 0; i < this.files.length; i++) {
        if (this.files[i].id === fileId) {
          this.files.splice(i, 1)
          console.debug('Deleted file', fileId, 'from vuex')
        }
      }
    },
    deleteFile(fileId) {
      this.clearError()
      axios.delete(backendUrls.piecejointe(fileId))
        .then(() => {
          this.deleteFileFromVuex(fileId)
        })
        .catch((error) => {
          console.log('Error when deleting question file', error)
          this.errorMessage = 'Le fichier n\'a pu être supprimé.'
        })
    },
  },
})
</script>
