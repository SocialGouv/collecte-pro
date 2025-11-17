<template>
  <div>
    <success-bar v-if="notification.type === 'success'" @dismissed="clearNotification">
      <p>
        Le fichier "{{ notification.filename }}" a bien été envoyé à la corbeille.
        <a :href="trashUrl">Cliquez ici</a> pour le voir dans la corbeille.
      </p>
    </success-bar>

    <error-bar v-if="notification.type === 'error'" @dismissed="clearNotification">
      <p>{{ notification.message }}</p>
    </error-bar>

    <div class="table-responsive question-box-child" v-if="filesList.length">
      <div class="form-label">
        Fichier{{ answer_count===1 ? '': 's' }} déposé{{ answer_count===1 ? '': 's' }}:
      </div>
      <table class="response-file-list table table-hover table-outline table-vcenter text-nowrap card-table">
        <thead>
          <tr>
            <th class="date-column">Date de dépôt</th>
            <th>Nom du document</th>
            <th class="deposant-column">Déposant</th>
            <th class="corbeille-column" v-if="isAudited">Mettre à la corbeille</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="file in filesList" :key="file.id">
            <td>
              <div>{{ file.creation_date }}</div>
              <div class="small text-muted">{{ file.creation_time }}</div>
            </td>
            <td>
              <a target="_blank" rel="noopener noreferrer" :href="file.url">{{ file.basename }}</a>
            </td>
            <td>{{ file.author.first_name }} {{ file.author.last_name }}</td>
            <td v-if="isAudited">
              <button
                data-bs-toggle="modal"
                :data-bs-target="'#trash-confirm-modal-' + file.id"
                class="btn btn-outline-primary"
              >
                <i class="fe fe-trash-2" aria-hidden="true"></i>
                <span class="sr-only">Mettre à la corbeille</span>
              </button>
            </td>
          </tr>
        </tbody>
      </table>

      <confirm-modal
        v-for="file in filesList"
        :key="file.id"
        :id="'trash-confirm-modal-' + file.id"
        title="Corbeille"
        confirm-button="Oui, envoyer à la corbeille"
        cancel-button="Non, annuler"
        @confirm="sendToTrash(file)"
      >
        <p>Vous allez envoyer “{{ file.basename }}” à la corbeille.</p>
      </confirm-modal>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue'
import axios from 'axios'
import backendUrls from '../utils/backend'
import { clearCache } from '../utils/utils'
import ConfirmModal from '../utils/ConfirmModal'
import ErrorBar from '../utils/ErrorBar'
import SuccessBar from '../utils/SuccessBar'
import EventBus from '../events'
import DateFormat from '../utils/DateFormat.js'

axios.defaults.xsrfCookieName = 'csrftoken'
axios.defaults.xsrfHeaderName = 'X-CSRFTOKEN'

const EVENT_NAME = 'response-files-updated-'

export default defineComponent({
  name: 'ResponseFileList',
  props: {
    question: { type: Object, required: true },
    questionnaireId: { type: Number, required: true },
    isAudited: { type: Boolean, required: true },
  },
  components: { ConfirmModal, ErrorBar, SuccessBar },
  data() {
    return {
      notification: {
        type: '', // 'success' | 'error'
        filename: '',
        message: '',
      },
    }
  },
  computed: {
    filesList(): Array<any> {
      return (this.question.response_files || [])
        .filter(f => !f.is_deleted)
        .sort((a, b) => new Date(a.created).getTime() - new Date(b.created).getTime())
    },
    answer_count(): number {
      return this.filesList.length
    },
    trashUrl(): string {
      return backendUrls.trash(this.questionnaireId)
    },
  },
  mounted() {
    EventBus.$on(EVENT_NAME + this.question.id, (files) => {
      this.question.response_files = files
    })
  },
  methods: {
    sendToTrash(file: any) {
      this.clearNotification()
      const formData = new FormData()
      formData.append('is_deleted', 'true')

      axios.put(backendUrls.responseFileTrash(file.id), formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
      .then(() => {
        clearCache()
        file.is_deleted = true
        EventBus.$emit(EVENT_NAME + this.question.id, this.question.response_files)
        this.showSuccess(file.basename)
      })
      .catch((error) => {
        console.error('Error sending file to trash', error)
        this.showError(`Le fichier n'a pu être envoyé à la corbeille. Erreur : ${error}`)
      })
    },
    showSuccess(filename: string) {
      this.notification.type = 'success'
      this.notification.filename = filename
    },
    showError(message: string) {
      this.notification.type = 'error'
      this.notification.message = message
    },
    clearNotification() {
      this.notification.type = ''
      this.notification.filename = ''
      this.notification.message = ''
    },
  },
})
</script>
