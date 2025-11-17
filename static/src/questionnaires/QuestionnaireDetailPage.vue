<template>
  <div class="mx-3">
    <breadcrumbs :control="control"></breadcrumbs>

    <!-- Loader ou erreur d'accès -->
    <div v-if="!isLoaded">
      <p>Chargement des droits d’accès…</p>
    </div>
    <error-bar v-else-if="accessError">
      <p>{{ accessError }}</p>
    </error-bar>

    <template v-else>
      <!-- Bouton demande de droits si brouillon -->
      <request-editor-button 
        v-if="accessType === 'demandeur' && questionnaire.is_draft"
        :questionnaire='questionnaire'>
      </request-editor-button>
      <success-bar v-else-if="accessType === 'demandeur' && !questionnaire.is_draft">
        Ce questionnaire est publié : il est visible par l'organisme interrogé et n'est plus
        modifiable.
      </success-bar>

      <!-- En-tête du questionnaire -->
      <div class="page-header">
        <h2 class="page-title">
          <span class="fe fe-list mr-2" aria-hidden="true"></span>
          <span v-if="statusTag" 
                :class="['tag', `tag-${statusTag.color}`, 'round-tag', 'font-italic', 'mr-2']">
            {{ statusTag.label }}
          </span>
          {{ questionnaire.title_display }}
        </h2>
      </div>

      <div :class="{ preview: questionnaire.is_draft }">
        <questionnaire-metadata 
          :questionnaire="questionnaire" 
          :control="control" 
          :with-trash="!questionnaire.is_draft" 
          :accessType="accessType">
        </questionnaire-metadata>

        <div>
          <theme-box v-for="(theme, themeIndex) in questionnaire.themes"
                     :key="theme.id"
                     :theme="theme"
                     :theme-numbering="themeIndex + 1">

            <question-box v-for="(question, qIndex) in theme.questions"
                          :key="question.id"
                          :with-collapse="true"
                          :theme-numbering="themeIndex + 1"
                          :question-numbering="qIndex + 1"
                          :question="question">

              <question-file-list :files="question.question_files">
              </question-file-list>

              <response-file-list :question="question"
                                  :questionnaire-id="questionnaire.id"
                                  :is-audited="accessType === 'repondant'">
              </response-file-list>

              <response-dropzone :is-audited="accessType === 'repondant'"
                                 :question-id="question.id">
              </response-dropzone>

            </question-box>

          </theme-box>
        </div>
      </div>

      <update-date-reponse-modal 
        :questionnaireId="questionnaireId" 
        :questionnaire="questionnaire">
      </update-date-reponse-modal>
    </template>
  </div>
</template>

<script lang="ts">
import { defineComponent, computed, onMounted } from 'vue'
import { useStore } from 'vuex'
import axios from 'axios'
import backendUrls from '../utils/backend'
import { loadStatuses } from '../store'

import Breadcrumbs from '../utils/Breadcrumbs'
import QuestionBox from '../questions/QuestionBox'
import QuestionFileList from '../questions/QuestionFileList'
import QuestionnaireMetadata from './QuestionnaireMetadata'
import RequestEditorButton from '../editors/RequestEditorButton'
import ResponseDropzone from '../questions/ResponseDropzone'
import ResponseFileList from '../questions/ResponseFileList'
import SuccessBar from '../utils/SuccessBar'
import ThemeBox from '../themes/ThemeBox'
import UpdateDateReponseModal from '../questionnaires/UpdateDateReponseModal'
import ErrorBar from '../utils/ErrorBar'

export default defineComponent({
  name: 'QuestionnaireDetailPage',
  props: {
    controlId: { type: Number, required: true },
    questionnaireId: { type: Number, required: true },
  },
  components: {
    Breadcrumbs,
    QuestionBox,
    QuestionFileList,
    QuestionnaireMetadata,
    RequestEditorButton,
    ResponseDropzone,
    ResponseFileList,
    SuccessBar,
    ThemeBox,
    UpdateDateReponseModal,
    ErrorBar,
  },
  setup(props) {
    const store = useStore()
    const accessType = ref('')
    const accessError = ref<string | null>(null)

    const controls = computed(() => store.state.controls)
    const userLoadStatus = computed(() => store.state.sessionUserLoadStatus)
    const isLoaded = computed(() => userLoadStatus.value === loadStatuses.SUCCESS)
    const control = computed(() => controls.value.find(c => c.id === props.controlId))
    const questionnaire = computed(() => control.value?.questionnaires.find(q => q.id === props.questionnaireId))

    const statusTag = computed(() => {
      if (!isLoaded.value || accessType.value !== 'demandeur') return null
      const q = questionnaire.value
      if (!q) return null
      if (q.is_draft) return { color: 'azure', label: 'Brouillon' }
      if (q.has_replies && !q.is_replied) return { color: 'yellow', label: 'En cours' }
      if (q.is_replied && !q.is_finalized) return { color: 'orange', label: 'Répondu' }
      if (q.is_finalized) return { color: 'purple', label: 'Finalisé' }
      return { color: 'green', label: 'Publié' }
    })

    const getAccessType = async () => {
      try {
        const resp = await axios.get(backendUrls.getAccessToControl(props.controlId))
        accessType.value = resp.data?.[0]?.access_type || ''
      } catch (error) {
        console.error('Erreur sur l\'access type :', error)
        accessError.value = 'Impossible de récupérer les droits d’accès.'
      }
    }

    onMounted(getAccessType)

    return {
      accessType,
      accessError,
      controls,
      userLoadStatus,
      isLoaded,
      control,
      questionnaire,
      statusTag,
    }
  }
})
</script>
