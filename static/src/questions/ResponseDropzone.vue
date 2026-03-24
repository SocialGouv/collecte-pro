<template>
  <div :id="'dropzone_' + questionId" class="response-dropzone">
    <div v-show="isAudited" class="form-group question-box-child">
      <div class="form-label">Déposer vos réponses</div>

      <ErrorBar v-if="hasErrors" @dismissed="clearErrors">
        <p>Une erreur s'est produite lors de la transmission d'un fichier.</p>
      </ErrorBar>

      <form :action="uploadUrl"
            method="post"
            enctype="multipart/form-data"
            :id="'dropzone-area-' + questionId"
            ref="dropzoneArea"
            class="dropzone">
        
        <input :id="'csrf-token-' + questionId" type="hidden" name="csrfmiddlewaretoken" :value="csrftoken" aria-label="CSRF Token" role="presentation">
        <div class="dz-message" data-dz-message>
          <button type="button" class="btn" :aria-label="'Importer des fichiers pour la question ' + questionId">Cliquer ou glisser-déposer vos fichiers.</button>
        </div>
        
        <input :id="'question-id-' + questionId" type="hidden" name="question_id" :value="questionId" aria-label="ID de la question" role="presentation"/>
        <div class="fallback">
          <label :id="'file-label-' + questionId" :for="'file-input-' + questionId">
            Sélectionner un fichier
          </label>
          <input :id="'file-input-' + questionId" name="file" type="file" :aria-labelledby="'file-label-' + questionId"/>
        </div>
      </form>

      <div class="text-right">
        <span class="dropdown-icon fe fe-help-circle" aria-hidden="true"></span>
        <a :href="faqUrl">Des questions sur le dépôt de fichiers ?</a>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted } from 'vue'
import Dropzone from 'dropzone'
import 'dropzone/dist/basic.css'
import 'dropzone/dist/dropzone.css'
import axios from 'axios'
import backendUrls from '../utils/backend'
import { clearCache } from '../utils/utils'
import EventBus from '../events'
import ErrorBar from '../utils/ErrorBar'

axios.defaults.xsrfCookieName = 'csrftoken'
axios.defaults.xsrfHeaderName = 'X-CSRFTOKEN'

const UPLOAD_TIMEOUT_MS = 3 * 60 * 1000 // 3 min

export default defineComponent({
  name: 'ResponseDropzone',
  props: {
    isAudited: { type: Boolean, required: true },
    questionId: { type: Number, required: true },
  },
  components: { ErrorBar },
  setup(props) {
    const faqUrl = backendUrls.faq()
    const uploadUrl = backendUrls.upload()
    const csrftoken = ref('')
    const hasErrors = ref(false)
    const errorMessage = ref('')
    const dropzoneArea = ref<HTMLFormElement | null>(null)

    const readCookie = (name: string) => {
      const nameEQ = name + '='
      const ca = document.cookie.split(';')
      for (let c of ca) {
        c = c.trim()
        if (c.indexOf(nameEQ) === 0) return c.substring(nameEQ.length)
      }
      return ''
    }

    const clearErrors = () => {
      hasErrors.value = false
      errorMessage.value = ''
    }

    const styleSuccess = (file: any) => {
      const pathEl = file.previewElement.querySelector('.dz-success-mark g path')
      if (pathEl) pathEl.setAttribute('fill', '#5EBB00')
      const removeBtn = file.previewElement.querySelector('.dz-remove')
      removeBtn?.remove()
    }

    const styleError = (file: any) => {
      const pathEl = file.previewElement.querySelector('.dz-error-mark g g')
      if (pathEl) pathEl.setAttribute('fill', '#cd201f')
      const removeBtn = file.previewElement.querySelector('.dz-remove')
      removeBtn?.remove()
    }

    const styleTimeout = (file: any, message: string) => {
      file.previewElement.classList.add('dz-error')
      file.previewElement.classList.remove('dz-processing')
      const progressEl = file.previewElement.querySelector('.dz-progress')
      progressEl?.remove()
      const errorMessageEl = file.previewElement.querySelector('.dz-error-message span')
      if (errorMessageEl) errorMessageEl.textContent = message
      styleError(file)
    }

    const dropzoneTimeoutCallback = (file: any, error: any) => {
      clearCache()
      hasErrors.value = true
      errorMessage.value = `L'envoi du fichier "${file.name}" a mis plus de ${UPLOAD_TIMEOUT_MS / 1000} secondes et a été annulé.`
      styleTimeout(file, errorMessage.value)
    }

    const fetchQuestionData = async () => {
      const response = await axios.get(backendUrls.question(props.questionId))
      return response.data.response_files
    }

    const dropzoneSuccessCallback = async (file: any) => {
      clearCache()
      styleSuccess(file)
      const dz = Dropzone.forElement(dropzoneArea.value!)
      dz.removeAllFiles(true)

      const responseFiles = await fetchQuestionData()
      EventBus.$emit('response-files-updated-' + props.questionId, responseFiles)
    }

    const dropzoneErrorCallback = (file: any, message: string) => {
      clearCache()
      if (file.status !== 'canceled') {
        hasErrors.value = true
        errorMessage.value = message
      }
      styleError(file)
      console.debug('Error when uploading response file.', file, message)
    }

    onMounted(() => {
      csrftoken.value = readCookie('csrftoken')

      if (!dropzoneArea.value) return

      
      new Dropzone(dropzoneArea.value, {
        addRemoveLinks: true,
        timeout: UPLOAD_TIMEOUT_MS,
        maxFiles: 1,
        init: function() {
          this.on('success', dropzoneSuccessCallback)
          this.on('error', dropzoneErrorCallback)
          this.on('addedfile', clearErrors)
          this.on('sending', (file, xhr) => {
            xhr.ontimeout = (error) => dropzoneTimeoutCallback(file, error)
          })
        },
        dictCancelUpload: "Annuler l'envoi",
        dictUploadCanceled: "L'envoi a été annulé.",
        dictCancelUploadConfirmation: "Etes-vous sûr.e de vouloir annuler l'envoi?",
        dictRemoveFile: 'Retirer le fichier',
        dictFileTooBig: 'La taille du fichier dépasse la limite authorisée.',
        dictMaxFilesExceeded: 'Vous ne pouvez déposer qu\'un seul fichier à la fois.',
      })
    })

    return {
      faqUrl,
      uploadUrl,
      csrftoken,
      hasErrors,
      errorMessage,
      clearErrors,
      dropzoneArea,
    }
  },
})
</script>
