<template>
  <div class="mx-3">
    <breadcrumbs :control="control"></breadcrumbs>
    <template v-if="isLoaded && accessType === 'demandeur'">
      <request-editor-button :questionnaire='questionnaire' v-if="questionnaire.is_draft">
      </request-editor-button>
      <success-bar v-else>
        Ce questionnaire est publié : il est visible par l'organisme interrogé et n'est plus
        modifiable.
      </success-bar>
    </template>

    <div class="page-header">
      <h2 class="page-title">
        <span class="fe fe-list mr-2" aria-hidden="true"></span>
        <template v-if="isLoaded && accessType === 'demandeur'">
          <span v-if="questionnaire.is_draft"
                class="tag tag-azure big-tag round-tag font-italic mr-2">
            Brouillon
          </span>
          <span v-else-if="questionnaire.has_replies && !questionnaire.is_replied" class="tag tag-yellow round-tag font-italic mr-2">En cours</span>
          <span v-else-if="questionnaire.is_replied && !questionnaire.is_finalized" class="tag tag-orange round-tag font-italic mr-2">Répondu</span>
          <span v-else-if="questionnaire.is_finalized" class="tag tag-purple round-tag font-italic mr-2">Finalisé</span>
          <span v-else class="tag tag-green big-tag round-tag font-italic mr-2">Publié</span>
        </template>
        {{ questionnaire.title_display }}
      </h2>
    </div>
    <div :class="{ preview: questionnaire.is_draft }">
      <questionnaire-metadata :questionnaire="questionnaire" :control="control" :with-trash="!questionnaire.is_draft" :accessType="accessType">
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
                                :is-audited="isLoaded && accessType === 'repondant'">
            </response-file-list>
            <response-dropzone :is-audited="isLoaded && accessType === 'repondant'"
                               :question-id="question.id">
            </response-dropzone>

          </question-box>

        </theme-box>

      </div>
    </div>
    <update-date-reponse-modal :questionnaireId="questionnaireId" :questionnaire="questionnaire">
    </update-date-reponse-modal>
  </div>
</template>

<script>
import Vue from 'vue'

import Breadcrumbs from '../utils/Breadcrumbs'
import { loadStatuses } from '../store'
import { mapState } from 'vuex'
import QuestionBox from '../questions/QuestionBox'
import QuestionFileList from '../questions/QuestionFileList'
import QuestionnaireMetadata from './QuestionnaireMetadata'
import RequestEditorButton from '../editors/RequestEditorButton'
import ResponseDropzone from '../questions/ResponseDropzone'
import ResponseFileList from '../questions/ResponseFileList'
import SuccessBar from '../utils/SuccessBar'
import ThemeBox from '../themes/ThemeBox'
import UpdateDateReponseModal from '../questionnaires/UpdateDateReponseModal'

import axios from 'axios'
import backendUrls from '../utils/backend'

export default Vue.extend({
  name: 'QuestionnaireDetailPage',
  props: {
    controlId: Number,
    questionnaireId: Number,
  },
  data: function() {
    return {
      accessType: '',
    }
  },
  computed: {
    control() {
      return this.controls.find(control => control.id === this.controlId)
    },
    questionnaire() {
      return this.control.questionnaires.find(
        questionnaire => questionnaire.id === this.questionnaireId)
    },
    ...mapState({
      // Note : we don't map controlsLoadStatus, because the only use of
      // this component is within a page which pre-fetches the data from server, so we know it is
      // already there.
      controls: 'controls',
      user: 'sessionUser',
      userLoadStatus: 'sessionUserLoadStatus',
    }),
    isLoaded() {
      return this.userLoadStatus === loadStatuses.SUCCESS
    },
  },
  mounted() {
    this.getAccessType(this.control.id);
  },
  methods: {
    async getAccessType(controlId) {
      try {
        const resp = await axios.get(backendUrls.getAccessToControl(controlId))
        this.accessType = (
          resp.data &&
          resp.data[0] &&
          resp.data[0].access_type
        ) ? resp.data[0].access_type : ''
      } catch (error) {
        console.error("Erreur sur l'access type : ", error)
      }
    },
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
  },
})

</script>
