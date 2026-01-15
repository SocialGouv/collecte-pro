<template>
<div>
  <error-bar v-if="errorMessage" @dismissed="clearError">
    <p>{{ errorMessage }}</p>
  </error-bar>
  <div v-if="question.id">
    <label class="btn btn-primary" id="file-upload-label">
      <span class="fe fe-upload mr-2" aria-hidden="true"></span>
      Ajouter un fichier annexe
      <input type="file" ref="fileInput" v-on:change="handleFileUpload()" hidden aria-labelledby="file-upload-label"/>
    </label>
  </div>
  <div v-else>
    <label class="btn btn-primary disabled" >
      <span class="fe fe-upload mr-2" ></span>
      Ajouter un fichier annexe
    </label>
    <div class="small">
      Pour pouvoir ajouter des annexes,
    </div>
    <div class="small">
      vous devez d'abord enregistrer
    </div>
    <div class="small">
      votre brouillon.
    </div>
  </div>
</div>
</template>

<script lang="ts">
import { ref, defineComponent } from 'vue'
import axios from 'axios'
import backendUrls from '../utils/backend'
import ErrorBar from '../utils/ErrorBar.vue'

export default defineComponent({
  name: 'QuestionFileUpload',
  props: {
    question: {
      type: Object,
      required: true,
    },
  },
  components: {
    ErrorBar,
  },
  setup(props) {
    const errorMessage = ref<string | undefined>(undefined)
    const file = ref<File | null>(null)
    const fileInput = ref<HTMLInputElement | null>(null)

    const clearError = () => {
      errorMessage.value = undefined
    }

    const handleFileUpload = () => {
      if (!fileInput.value?.files) return
      file.value = fileInput.value.files[0]
      submitFile()
    }

    const submitFile = async () => {
      if (!file.value) return
      clearError()
      const formData = new FormData()
      formData.append('file', file.value)
      formData.append('question', String(props.question.id))
      
      try {
        const response = await axios.post(backendUrls.annexe(), formData, {
          headers: { 'Content-Type': 'multipart/form-data' },
        })
        const newFile = response.data
        props.question.question_files.push(newFile)
      } catch (error: any) {
        console.error('Error when posting question file', error)
        if (error.response && Array.isArray(error.response.data)) {
          errorMessage.value = error.response.data[0]
        } else {
          errorMessage.value = "L'annexe n'a pu être sauvée."
        }
      }
    }

    return {
      errorMessage,
      fileInput,
      handleFileUpload,
      clearError,
    }
  },
})
</script>
