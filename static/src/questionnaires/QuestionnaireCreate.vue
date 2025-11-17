<template>
<div>
  <a name="contenu"> </a>
  <div class="mx-3">
    <breadcrumbs v-if="state !== STATES.LOADING" :control="currentControl"></breadcrumbs>
    <swap-editor-button v-if="state !== STATES.LOADING && controlHasMultipleInspectors"
                        :control-id="controlId"
                        @save-draft="saveDraftAndSwapEditor">
    </swap-editor-button>
    <div class="page-header">
      <div class="page-title flex-wrap">
        <span class="fe fe-list mr-2" aria-hidden="true"></span>
        <span v-if="currentQuestionnaire.is_draft || currentQuestionnaire.id === undefined"
              class="tag tag-azure big-tag round-tag font-italic mr-2">
          Brouillon
        </span>
        <span>
          Rédaction du Questionnaire n°{{ questionnaireNumbering }}
        </span>
        <span v-if="currentQuestionnaire.title" class="ml-1">
          - {{ currentQuestionnaire.title }}
        </span>
      </div>
    </div>
    <div v-if="hasErrors" class="alert alert-danger" id="questionnaire-create-error" role="alert">
      {{ errorMessage }}
    </div>

    <div v-if="state === STATES.LOADING"
         class="card mt-9">
      <div class="card-body flex-column align-items-center">
        <div class="loader"></div>
        <div class="mt-4"> En chargement ... </div>
      </div>
    </div>
    <div v-else
         id="page-middle">
      <wizard id="wizard"
              :active-step-number="this.state"
              :step-titles="['Renseigner l\'introduction',
                            'Ajouter des questions',
                            'Aperçu avant publication']"
              @next="next"
              @previous="back">
      </wizard>

      <questionnaire-metadata-create
              id="questionnaire-metadata-create"
              ref="questionnaireMetadataCreate"
              :questionnaire-numbering="questionnaireNumbering"
              :questionnaire="currentQuestionnaire"
              v-show="state === STATES.START">
      </questionnaire-metadata-create>
      <questionnaire-body-create
              id="questionnaire-body-create"
              ref="questionnaireBodyCreate"
              v-show="state === STATES.CREATING_BODY">
      </questionnaire-body-create>
      <questionnaire-preview
              id="questionnaire-preview"
              v-show="state === STATES.PREVIEW">
      </questionnaire-preview>
    </div>
  </div>


  <div id="bottom-bar"
       v-show="state !== STATES.LOADING"
       class="flex-column bg-white sticky-bottom border-top p-4">
    <div id="button-bar" class="flex-row justify-content-between">
      <button id="go-home-button"
              type="button"
              class="btn btn-secondary"
              @click="saveDraftAndGoHome"
      >
        <span class="fa fa-chevron-left mr-2" aria-hidden="true"></span>
        Retour
      </button>
      <div>
        <button v-if="state !== STATES.START"
                id="back-button"
                @click="back"
                class="btn btn-secondary">
          <span class="fa fa-chevron-left mr-2" aria-hidden="true"></span>
          Etape {{ state - 1 }}
        </button>
        <button v-if="state === STATES.CREATING_BODY"
                id="move-themes-button"
                role="button"
                type="button"
                class="btn btn-secondary"
                @click="saveAndShowMoveThemesModal"
                title="Réorganiser les thèmes">
          <span class="fa fa-exchange-alt fa-rotate-90" aria-hidden="true"></span>
          Réorganiser les thèmes
        </button>
        <button @click="validateFormAndSaveDraft"
                class="btn btn-primary">
          <span class="fe fe-save" aria-hidden="true"></span>
          Enregistrer
        </button>
        <button v-if="state !== STATES.PREVIEW"
                id="next-button"
                @click="next"
                class="btn btn-secondary">
          Etape {{ state + 1 }}
          <span class="fa fa-chevron-right ml-2" aria-hidden="true"></span>
        </button>
        <button v-if="state === STATES.PREVIEW"
                id="publishButton"
                ref="publishButton"
                @click="startPublishFlow()"
                class="btn btn-primary ml-5"
                title="Publier le questionnaire à l'organisme interrogé">
          <span class="fa fa-rocket mr-1" aria-hidden="true"></span>
          Publier
        </button>
      </div>
    </div>
    <div class="flex-row justify-content-end mt-2">
      <div v-if="saveMessage.isWaitingForMinDisplayTime || saveMessage.isSaveHappening"
           class="save-message">
        <span class="fas fa-sync-alt mr-2" aria-hidden="true"></span>
        Enregistrement en cours ...
      </div>
      <div v-else
           :class="{ 'text-danger': hasErrors, 'text-muted': !hasErrors }"
           class="flex-row align-items-center save-message">
        <span v-if="hasErrors" class="fe fe-alert-triangle mr-2" aria-hidden="true"></span>
        <span v-else class="fe fe-check-circle mr-2" aria-hidden="true"></span>
        {{ saveMessage.text }}
      </div>
    </div>
  </div>

  <publish-flow ref="publishFlow"
                :publishFunction="publish"
                :questionnaire="currentQuestionnaire"
                :controlId="controlId">
  </publish-flow>

</div>
</template>

<script>
import '../../css/questionnaires.css'
import axios from 'axios'
import backend from '../utils/backend'
import { nowTimeString, toBackendFormat } from '../utils/DateFormat'
import Breadcrumbs from '../utils/Breadcrumbs'
import { loadStatuses } from '../store'
import PublishFlow from './PublishFlow'
import QuestionnaireBodyCreate from './QuestionnaireBodyCreate'
import QuestionnaireMetadataCreate from './QuestionnaireMetadataCreate'
import QuestionnairePreview from './QuestionnairePreview'
import StickyBottomMixin from '../utils/StickyBottomMixin'
import SwapEditorButton from '../editors/SwapEditorButton'
import { computed, reactive, ref, onMounted } from 'vue'
import { useStore } from 'vuex'
import Wizard from '../utils/Wizard'
import backendUrls from '../utils/backend'

const STATES = {
  LOADING: 0,
  START: 1,
  CREATING_BODY: 2,
  PREVIEW: 3,
}
const SAVING_MESSAGE_MIN_DISPLAY_TIME_MILLIS = 2000

axios.defaults.xsrfCookieName = 'csrftoken'
axios.defaults.xsrfHeaderName = 'X-CSRFTOKEN'

export default {
  props: {
    controlId: Number,
    controlHasMultipleInspectors: Boolean,
    questionnaireId: Number,
    questionnaireNumbering: Number,
    window: { default: () => window },
  },
  setup(props, { emit }) {
    const store = useStore()

    // Reactive state
    const state = reactive({
      errorMessage: '',
      errors: [],
      hasErrors: false,
      userId: '',
      STATES: STATES,
      state: STATES.LOADING,
      saveMessage: {
        text: '',
        isWaitingForMinDisplayTime: false,
        isSaveHappening: false,
      },
      questionnaire: '',
      control: null,
    })

    // Remplacement de mapFields
    const controls = computed({
      get: () => store.state.controls,
      set: (val) => store.commit('updateControls', val),
    })
    const controlsLoadStatus = computed({
      get: () => store.state.controlsLoadStatus,
      set: (val) => store.commit('updateControlsLoadStatus', val),
    })
    const currentQuestionnaire = computed({
      get: () => store.state.currentQuestionnaire,
      set: (val) => store.commit('updateCurrentQuestionnaire', val),
    })

    const currentControl = computed(() => {
      if (!currentQuestionnaire.value || !currentQuestionnaire.value.control) return null
      return controls.value.find(c => c.id === currentQuestionnaire.value.control)
    })

    // --------- Methods ---------
    const emitQuestionnaireUpdated = () => emit('questionnaire-updated', currentQuestionnaire.value)

    const displayErrors = (msg, errs) => {
      state.hasErrors = true
      state.errors = errs || []
      state.errorMessage = errs ? `${msg} Erreurs : ${JSON.stringify(errs)}` : msg
      console.error(state.errorMessage)
    }

    const clearErrors = () => {
      state.hasErrors = false
      state.errors = []
      state.errorMessage = ''
    }

    const moveToState = (newState) => {
      clearErrors()
      state.state = newState
    }

    const findCurrentQuestionnaire = (controlsList, questionnaireId) => {
      for (const control of controlsList) {
        const found = control.questionnaires.find(q => q.id === questionnaireId)
        if (found) {
          state.questionnaire = found
          return found
        }
      }
    }

    const loadNewQuestionnaire = () => {
      const newQ = {
        control: props.controlId,
        description: QuestionnaireMetadataCreate.DESCRIPTION_DEFAULT,
        title: '',
        themes: [],
      }
      currentQuestionnaire.value = newQ
      emitQuestionnaireUpdated()
      moveToState(STATES.START)
    }

    const loadExistingQuestionnaire = async () => {
      const curQ = findCurrentQuestionnaire(controls.value, props.questionnaireId)
      if (!curQ) {
        displayErrors(`Le questionnaire ${props.questionnaireId} n'a pas été trouvé.`)
        throw new Error('Questionnaire not found')
      }
      if (!curQ.is_draft) {
        displayErrors(`Le questionnaire ${props.questionnaireId} n'est pas un brouillon.`)
        throw new Error('Questionnaire is not a draft')
      }
      currentQuestionnaire.value = curQ
      currentQuestionnaire.value.control = props.controlId

      const resp = await axios.get(backendUrls.getQuestionnaireAndThemesByCtlId(props.controlId))
      state.control = resp.data.find(obj => obj.id === props.controlId)
      const curQFull = state.control.questionnaires.find(q => q.id === props.questionnaireId)
      const themes = curQFull.themes.map(t => {
        const questions = t.questions.map(q => ({
          ...q,
          question_files: q.question_files.map(ff => ({
            id: ff.id, url: ff.url, basename: ff.basename, file: ff.file, question: ff.question
          }))
        }))
        return { ...t, questions }
      })
      currentQuestionnaire.value.themes = themes
      currentQuestionnaire.value.description = curQFull.description
      currentQuestionnaire.value.questionnaire_files = curQFull.questionnaire_files

      emitQuestionnaireUpdated()
      moveToState(STATES.START)
    }

    const validateCurrentForm = () => {
      if (state.state === STATES.PREVIEW) return true
      if (state.state === STATES.START) return refs.questionnaireMetadataCreate.validateForm()
      if (state.state === STATES.CREATING_BODY) return refs.questionnaireBodyCreate.validateForm()
    }

    // --------- Lifecycle ---------
    onMounted(() => {
      if (!props.questionnaireId) loadNewQuestionnaire()
      else loadExistingQuestionnaire()
      if (!props.controlId && !props.questionnaireId) {
        throw new Error('QuestionnaireCreate needs a controlId or a questionnaireId')
      }
    })

    return {
      state,
      controls,
      controlsLoadStatus,
      currentQuestionnaire,
      currentControl,
      emitQuestionnaireUpdated,
      displayErrors,
      clearErrors,
      moveToState,
      loadNewQuestionnaire,
      loadExistingQuestionnaire,
      findCurrentQuestionnaire,
      validateCurrentForm,
    }
  },
  components: {
    Breadcrumbs,
    PublishFlow,
    QuestionnaireBodyCreate,
    QuestionnaireMetadataCreate,
    QuestionnairePreview,
    SwapEditorButton,
    Wizard,
  },
  mixins: [StickyBottomMixin],
}
</script>

