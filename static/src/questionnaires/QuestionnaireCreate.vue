<template>
<div>
  <span id="contenu" class="sr-only">Début du contenu principal</span>
  <div class="mx-3">
    <breadcrumbs v-if="state !== STATES.LOADING" :control="currentControl"></breadcrumbs>
    <swap-editor-button v-if="state !== STATES.LOADING && controlHasMultipleInspectors"
                        :control-id="controlId"
                        @save-draft="saveDraftAndSwapEditor"
                        aria-label="Changer d'éditeur">
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

  <!-- Note : use v-show and not v-if for the bottom-bar, because the element needs to be in the DOM
  from the start for the IE sticky-bottom to work. -->
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
import { loadStatuses, useStore } from '../store'
import PublishFlow from './PublishFlow'
import QuestionnaireBodyCreate from './QuestionnaireBodyCreate'
import QuestionnaireMetadataCreate from './QuestionnaireMetadataCreate'
import QuestionnairePreview from './QuestionnairePreview'
import StickyBottomMixin from '../utils/StickyBottomMixin'
import SwapEditorButton from '../editors/SwapEditorButton'
import { defineComponent, computed, ref } from 'vue'
import Wizard from '../utils/Wizard'
import backendUrls from '../utils/backend'

// State machine
const STATES = {
  LOADING: 0,
  START: 1,
  CREATING_BODY: 2,
  PREVIEW: 3,
}
const SAVING_MESSAGE_MIN_DISPLAY_TIME_MILLIS = 2000

axios.defaults.xsrfCookieName = 'csrftoken'
axios.defaults.xsrfHeaderName = 'X-CSRFTOKEN'

export default defineComponent({
  props: {
    controlId: Number,
    controlHasMultipleInspectors: Boolean,
    questionnaireId: Number,
    questionnaireNumbering: Number,
    // Pass window dependency for testing
    window: {
      default: () => window,
    },
  },
  data() {
    return {
      errorMessage: '',
      errors: [],
      hasErrors: false,
      userId:'',
      STATES: STATES,
      state: STATES.LOADING,
      saveMessage: {
        text: '',
        isWaitingForMinDisplayTime: false,
        isSaveHappening: false,
      },
      questionnaire: '',
    }
  },
  computed: {
    controls() {
      // Replace with Vuex store access or prop as needed
      return this.$store.state.controls
    },
    controlsLoadStatus() {
      return this.$store.state.controlsLoadStatus
    },
    currentQuestionnaire: {
      get() {
        return this.$store.state.currentQuestionnaire
      },
      set(val) {
        this.$store.commit('setCurrentQuestionnaire', val)
      }
    },
    currentControl() {
      if (!this.currentQuestionnaire || !this.currentQuestionnaire.control) {
        return null
      }
      return this.controls.find(control => control.id === this.currentQuestionnaire.control)
    },
  },
  watch: {
    // Watch change of loadStatus coming from the store, to know when the data is ready.
    controlsLoadStatus(newValue, oldValue) {
      const loadNewQuestionnaire = () => {
        const newQuestionnaire = {
          control: this.controlId,
          description: QuestionnaireMetadataCreate.DESCRIPTION_DEFAULT,
          title: '',
          themes: [],
        }
        this.currentQuestionnaire = newQuestionnaire
        this.emitQuestionnaireUpdated()
        this.moveToState(STATES.START)
        return
      }

      const loadExistingQuestionnaire = () => {
        const currentQuestionnaire =
          this.findCurrentQuestionnaire(this.controls, this.questionnaireId)
        if (!currentQuestionnaire) {
          const errorMessage = 'Le questionnaire ' + this.questionnaireId + ' n\'a pas été trouvé.'
          this.displayErrors(errorMessage)
          throw new Error('Questionnaire ' + this.questionnaireId + ' not found')
        }
        if (!currentQuestionnaire.is_draft) {
          const errorMessage = 'Le questionnaire ' + this.questionnaireId +
                ' n\'est pas un brouillon. Vous ne pouvez pas le modifier.'
          this.displayErrors(errorMessage)
          throw new Error(
            'Questionnaire ' + this.questionnaireId + ' is not a draft, you cannot edit it')
        }
        this.currentQuestionnaire = currentQuestionnaire
        this.emitQuestionnaireUpdated()
        this.moveToState(STATES.START)
      }

      if (newValue === loadStatuses.ERROR) {
        const errorMessage =
          'Erreur lors du chargement des données. Le questionnaire ne peut être affiché.'
        this.displayErrors(errorMessage)
        throw new Error('Store status is ERROR. Not loading questionnaire.')
      }
      if (newValue === loadStatuses.SUCCESS) {
        if (typeof this.questionnaireId === 'undefined') {
          loadNewQuestionnaire()
          return
        }
        loadExistingQuestionnaire()
      }
    },
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
  mixins: [
    StickyBottomMixin,
  ],
  mounted() {
    if (typeof this.questionnaireId === 'undefined') {
      this.loadNewQuestionnaire()
    } else {
      this.loadExistingQuestionnaire()
    }
    this.stickyBottom_makeStickyBottom('bottom-bar', 140, 103, 44)
    if (this.controlId === undefined && this.questionnaireId === undefined) {
      throw Error('QuestionnaireCreate needs a controlId or a questionnaireId')
    }
  },
  methods: {
    loadNewQuestionnaire() {
      const newQuestionnaire = {
        control: this.controlId,
        description: QuestionnaireMetadataCreate.DESCRIPTION_DEFAULT,
        title: '',
        themes: [],
      }
      this.currentQuestionnaire = newQuestionnaire
      this.emitQuestionnaireUpdated()
      this.moveToState(STATES.START)
    },
    async loadExistingQuestionnaire() {
      const currentQuestionnaire = this.findCurrentQuestionnaire(this.controls, this.questionnaireId)
      if (!currentQuestionnaire) {
        const errorMessage = 'Le questionnaire ' + this.questionnaireId + ' n\'a pas été trouvé.'
        this.displayErrors(errorMessage)
        throw new Error('Questionnaire ' + this.questionnaireId + ' not found')
      }
      if (!currentQuestionnaire.is_draft) {
        const errorMessage = 'Le questionnaire ' + this.questionnaireId +
          ' n\'est pas un brouillon. Vous ne pouvez pas le modifier.'
        this.displayErrors(errorMessage)
        throw new Error(
          'Questionnaire ' + this.questionnaireId + ' is not a draft, you cannot edit it')
      }
      this.currentQuestionnaire = currentQuestionnaire
      this.currentQuestionnaire.control = this.controlId
      const resp = await axios.get(backendUrls.getQuestionnaireAndThemesByCtlId(this.controlId))
      this.control = resp.data.filter(obj => obj.id === this.controlId)[0]
      const curQ = this.control.questionnaires.find(q => q.id === this.questionnaireId)
      const themes = curQ.themes.map(t => {
        const qq = t.questions.map(q => {
          const qf = q.question_files.map(ff => {
            return { id: ff.id, url: ff.url, basename: ff.basename, file: ff.file, question: ff.question }
          })
          return { description: q.description, id: q.id, order: q.order, question_files: qf }
        })
        return { id: t.id, order: t.order, questionnaire: t.questionnaire, questions: qq, title: t.title }
      })
      this.currentQuestionnaire.questionnaire_files = curQ.questionnaire_files
      this.currentQuestionnaire.description = curQ.description
      this.currentQuestionnaire.themes = themes
      this.emitQuestionnaireUpdated()
      this.moveToState(STATES.START)
    },
    findCurrentQuestionnaire(controls, questionnaireId) {
      for (let i = 0; i < controls.length; i++) {
        const control = controls[i]
        const foundQuestionnaires = control.questionnaires.filter(questionnaire => questionnaire.id === questionnaireId)
        if (foundQuestionnaires.length > 0) {
          this.questionnaire = foundQuestionnaires[0]
          return foundQuestionnaires[0]
        }
      }
    },
    emitQuestionnaireUpdated() {
      this.$emit('questionnaire-updated', this.currentQuestionnaire)
    },
    moveToState(newState) {
      this.clearErrors()
      this.state = newState
    },
    next() {
      if (this.state === STATES.START) {
        // Valider le formulaire HTML5 d'abord
        const visibleForm = document.querySelector('#questionnaire-metadata-create form')
        if (visibleForm && !visibleForm.checkValidity()) {
          visibleForm.reportValidity()
          return
        }
        // Puis valider les règles Vue
        if (!this.$refs.questionnaireMetadataCreate?.validateForm()) {
          return
        }
        this.saveDraft().then(() => {
          if (this.currentQuestionnaire.themes.length === 0) {
            this.currentQuestionnaire.themes.push({ questions: [{}] })
          }
          this.moveToState(STATES.CREATING_BODY)
        })
        return
      }
      if (this.state === STATES.CREATING_BODY) {
        // Valider le formulaire HTML5 d'abord
        const visibleForm = document.querySelector('#questionnaire-body-create form')
        if (visibleForm && !visibleForm.checkValidity()) {
          visibleForm.reportValidity()
          return
        }
        // Puis valider les règles Vue
        if (!this.$refs.questionnaireBodyCreate?.validateForm()) {
          return
        }
        this.saveDraft()
        this.moveToState(STATES.PREVIEW)
        return
      }
      console.error('Trying to go to "next", from state', this.state)
    },
    back(clickedStep) {
      if (this.state === STATES.CREATING_BODY) {
        // Valider le formulaire HTML5 d'abord
        const visibleForm = document.querySelector('#questionnaire-body-create form')
        if (visibleForm && !visibleForm.checkValidity()) {
          visibleForm.reportValidity()
          return
        }
        // Puis valider les règles Vue
        if (!this.$refs.questionnaireBodyCreate?.validateForm()) {
          return
        }
        this.saveDraft()
        this.moveToState(STATES.START)
        return
      }
      if (this.state === STATES.PREVIEW) {
        if (clickedStep === 1) {
          this.moveToState(STATES.START)
          return
        }
        if (clickedStep === 2) {
          this.moveToState(STATES.CREATING_BODY)
          return
        }
        this.moveToState(STATES.CREATING_BODY)
        return
      }
      console.error('Trying to go back from state', this.state, 'with clickedStep', clickedStep)
    },
    displayErrors(errorMessage, errors) {
      this.hasErrors = true
      this.errors = errors
      if (errors) {
        this.errorMessage = errorMessage + ' Erreurs : ' + JSON.stringify(errors)
      } else {
        this.errorMessage = errorMessage
      }
      console.error(errorMessage)
    },
    clearErrors() {
      this.hasErrors = false
      this.errors = []
      this.errorMessage = ''
    },
    _doSave() {
      const cleanPreSave = () => {
        if (this.currentQuestionnaire.end_date) {
          this.currentQuestionnaire.end_date = toBackendFormat(this.currentQuestionnaire.end_date)
        } else {
          delete this.currentQuestionnaire.end_date
        }
      }
      const getCreateMethod = () => axios.post.bind(this, backend.questionnaire())
      const getUpdateMethod = (questionnaireId) => axios.put.bind(this, backend.questionnaire(questionnaireId))
      this.clearErrors()
      cleanPreSave()
      let saveMethod
      if (this.currentQuestionnaire.id !== undefined) {
        saveMethod = getUpdateMethod(this.currentQuestionnaire.id)
      } else {
        saveMethod = getCreateMethod()
      }
      return saveMethod(this.currentQuestionnaire)
    },
    validateCurrentForm() {
      if (this.state === STATES.PREVIEW) {
        return true
      }
      if (this.state === STATES.START) {
        return this.$refs.questionnaireMetadataCreate?.validateForm() || false
      }
      if (this.state === STATES.CREATING_BODY) {
        return this.$refs.questionnaireBodyCreate?.validateForm() || false
      }
    },
    saveDraftAndSwapEditor() {
      if (!this.validateCurrentForm()) {
        return
      }
      this.saveDraft()
        .then(savedQuestionnaire => {
          this.$emit('show-swap-editor-modal', savedQuestionnaire.id)
        })
    },
    validateFormAndSaveDraft() {
      // Déclencher la validation HTML5 native du navigateur
      // Uniquement sur les formulaires visibles de l'étape active
      let visibleForm = null
      
      if (this.state === STATES.START) {
        visibleForm = document.querySelector('#questionnaire-metadata-create form')
      } else if (this.state === STATES.CREATING_BODY) {
        visibleForm = document.querySelector('#questionnaire-body-create form')
      }
      
      // Valider le formulaire visible si présent
      if (visibleForm && !visibleForm.checkValidity()) {
        // Déclencher l'affichage des messages de validation HTML5
        visibleForm.reportValidity()
        return
      }
      
      // Ensuite valider les règles personnalisées Vue
      if (!this.validateCurrentForm()) {
        return
      }
      
      this.saveDraft()
    },
    displaySaveInProgress() {
      this.saveMessage.isWaitingForMinDisplayTime = true
      setTimeout(() => { this.saveMessage.isWaitingForMinDisplayTime = false }, SAVING_MESSAGE_MIN_DISPLAY_TIME_MILLIS)
      this.saveMessage.isSaveHappening = true
    },
    displaySavingDone(dateDone) {
      this.saveMessage.text = 'Enregistrement fait à ' + dateDone + '.'
      this.saveMessage.isSaveHappening = false
    },
    displaySavingDoneWithError() {
      this.saveMessage.text = 'Erreur lors de la sauvegarde : les modifications ne sont pas enregistrées.'
      this.saveMessage.isWaitingForMinDisplayTime = false
      this.saveMessage.isSaveHappening = false
    },
    saveDraft() {
      this.currentQuestionnaire.is_draft = true
      this.displaySaveInProgress()
      return this._doSave()
        .then((response) => {
          this.currentQuestionnaire = response.data
          this.emitQuestionnaireUpdated()
          this.displaySavingDone(nowTimeString())
          return response.data
        })
        .catch((error) => {
          console.error('Error in draft save :', error)
          const errorToDisplay = (error.response && error.response.data) ? error.response.data : error
          this.displayErrors('Erreur lors de la sauvegarde du brouillon.', errorToDisplay)
          this.displaySavingDoneWithError()
        })
    },
    startPublishFlow() {
      if (this.$refs.publishFlow) {
        this.$refs.publishFlow.start()
      } else {
        console.error('publishFlow ref is not available')
      }
    },
    publish() {
      this.currentQuestionnaire.is_draft = false
      this.currentQuestionnaire.sent_date = toBackendFormat(new Date())
      return this._doSave()
    },
    saveDraftAndGoHome(event) {
      if (!this.validateCurrentForm()) {
        return
      }
      // Display a "loading" spinner on clicked button, while the user is redirected, so that they
      // know their click has been registered.
      $(event.target).addClass('btn-loading')
      this.saveDraft()
        .then(() => {
          this.goHome()
        })
    },
    saveAndShowMoveThemesModal() {
      // Valider le formulaire HTML5 d'abord
      let visibleForm = null
      
      if (this.state === STATES.CREATING_BODY) {
        visibleForm = document.querySelector('#questionnaire-body-create form')
      }
      
      // Valider le formulaire visible si présent
      if (visibleForm && !visibleForm.checkValidity()) {
        // Déclencher l'affichage des messages de validation HTML5
        visibleForm.reportValidity()
        return
      }
      
      // Ensuite valider les règles personnalisées Vue
      if (!this.validateCurrentForm()) {
        return
      }
      $('#move-themes-button').addClass('btn-loading')
      this.saveDraft()
        .then(() => {
          $('#move-themes-button').removeClass('btn-loading')
          if (this.state === STATES.CREATING_BODY && this.$refs.questionnaireBodyCreate?.$refs?.moveThemesModal?.$el) {
            $(this.$refs.questionnaireBodyCreate.$refs.moveThemesModal.$el).modal('show')
          }
        })
    },
  },
})
</script>