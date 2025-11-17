<template>
  <div class="card">
    <ConfirmModal
      ref="modal"
      cancel-button="Annuler"
      confirm-button="Dupliquer le questionnaire"
      title="Dupliquer un questionnaire"
      @confirm="cloneQuestionnaire"
    >
      <InfoBar>
        <p>Veuillez sélectionner les espaces de dépôt vers lesquels vous souhaitez dupliquer ce questionnaire.</p>
      </InfoBar>
      <form>
        <div class="form-group mb-6">
          <label v-for="ctrl in controls" :for="ctrl.id" :key="ctrl.id" class="custom-control custom-checkbox">
            <input :id="ctrl.id" type="checkbox" class="custom-control-input" :value="ctrl.id" v-model="checkedCtrls">
            <span class="custom-control-label">{{ ctrl.depositing_organization }} - {{ ctrl.title }} ({{ ctrl.reference_code }})</span>
          </label>
        </div>
      </form>
    </ConfirmModal>

    <div class="card-status card-status-top bg-blue"></div>
    <div class="card-header custom-card-header">
      <div class="float-right" v-if="hasAnyAnswerValue">
        <button @click="toggleView" class="card-title btn btn-primary ml-4 view-button" :title="isList ? 'Voir les documents' : 'Voir les questionnaires'">
          {{ isList ? 'Voir les documents' : 'Voir les questionnaires' }}
        </button>
      </div>
      <h2 class="card-title">
        <span class="fe fe-folder mr-2" :class="{ 'fe-list': isList }" aria-hidden="true"></span>
        <span>{{ isList ? 'Questionnaires' : 'Documents' }}</span>
      </h2>
    </div>

    <div v-if="currentView === 'questions'">
      <div v-if="accessibleQuestionnaires.length === 0" class="alert alert-icon alert-secondary m-2" role="status">
        <span class="fe fe-info mr-2" aria-hidden="true"></span>
        Il n'y a pas encore de questionnaire pour cet espace de dépôt.
      </div>
      <table v-else class="table card-table table-vcenter">
        <caption class="sr-only">Questionnaires</caption>
        <thead>
          <tr>
            <th v-if="accessType === 'demandeur'" scope="col">
              Statut
              <HelpTooltip text="Brouillon : modifiable, l'organisme interrogé ne le voit pas
Publié : non modifiable, l'organisme interrogé le voit
En cours : l'organisme interrogé a commencé à déposer les réponses
Répondu : l'organisme interrogé a fini de répondre au questionnaire
Finalisé : l'instruction des pièces déposées est achevée"/>
            </th>
            <th scope="col">Titre</th>
            <th scope="col">Date de réponse</th>
            <th v-if="accessType === 'demandeur'" scope="col">RRRRédacteur</th>
            <td class="border-bottom"></td>
          </tr>
        </thead>
        <tbody>
          <tr v-for="questionnaire in accessibleQuestionnaires" :key="'questionnaire-' + questionnaire.id">
            <td class="tag-column" v-if="accessType === 'demandeur'">
              <div v-if="questionnaire.is_draft" class="tag tag-azure round-tag font-italic">Brouillon</div>
              <div v-else-if="questionnaire.has_replies && !questionnaire.is_replied" class="tag tag-yellow round-tag font-italic">En cours</div>
              <div v-else-if="questionnaire.is_replied && !questionnaire.is_finalized" class="tag tag-orange round-tag font-italic">Répondu</div>
              <div v-else-if="questionnaire.is_finalized" class="tag tag-purple round-tag font-italic">Finalisé</div>
              <div v-else class="tag tag-green round-tag font-italic">Publié</div>
            </td>
            <td>
              <div>Questionnaire {{ questionnaire.numbering }}</div>
              <div>{{ questionnaire.title }}</div>
            </td>
            <td class="end-date-column">
              <small v-if="questionnaire.end_date">{{ formatDate(questionnaire.end_date) }}</small>
            </td>
            <td v-if="accessType === 'demandeur'" class="editor-column">
              <small v-if="questionnaire.editor">
                {{ questionnaire.editor.first_name }} {{ questionnaire.editor.last_name }}
                <span v-if="questionnaire.modified_date" class="text-muted editor-date">
                  {{ questionnaire.modified_date }} à {{ questionnaire.modified_time }}
                </span>
              </small>
            </td>
            <td class="w-1 action-column">
              <!-- Ici, conserver toute la logique des boutons, adaptée Vue 3 -->
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-if="currentView === 'tree'">
      <QuestionnaireTreeView :control="control"/>
    </div>

    <div v-if="accessType === 'demandeur'" class="card-footer flex-row justify-content-end">
      <a :href="questionnaireCreateUrl" class="btn btn-primary">
        <span class="fe fe-plus" aria-hidden="true"></span>
        Ajouter un questionnaire
      </a>
    </div>
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted } from 'vue'
import axios from 'axios'
import backendUrls from '../utils/backend'
import DateFormat from '../utils/DateFormat.js'
import HelpTooltip from '../utils/HelpTooltip'
import InfoBar from '../utils/InfoBar'
import ConfirmModal from '../utils/ConfirmModal'
import QuestionnaireTreeView from '../questionnaires/QuestionnaireTreeView'

export default {
  name: 'ControlDetail',
  props: ['control', 'user', 'accessType'],
  components: { HelpTooltip, InfoBar, ConfirmModal, QuestionnaireTreeView },
  setup(props) {
    const checkedCtrls = ref([])
    const currentView = ref('questions')
    const isList = ref(true)
    const hasAnyAnswerValue = ref(false)
    const control = reactive(props.control)
    
    const accessibleQuestionnaires = computed(() => {
      if (props.accessType === 'demandeur') return control.questionnaires
      return control.questionnaires.filter(q => !q.is_draft)
    })

    const questionnaireCreateUrl = computed(() => backendUrls['questionnaire-create'](control.id))

    const formatDate = (date) => DateFormat(date)

    const toggleView = () => {
      currentView.value = isList.value ? 'tree' : 'questions'
      isList.value = !isList.value
    }

    const checkAnyAnswer = async () => {
      try {
        const resp = await axios.get(backendUrls.getQuestionnaireAndThemesByCtlId(control.id))
        const ctl = resp.data.find(obj => obj.id === control.id)
        if (ctl) {
          Object.assign(control, ctl)
          hasAnyAnswerValue.value = accessibleQuestionnaires.value.some(q => q.has_replies)
        }
      } catch (error) {
        console.error(error)
        hasAnyAnswerValue.value = false
      }
    }

    onMounted(() => {
      checkAnyAnswer()
    })

    return {
      checkedCtrls, currentView, isList, hasAnyAnswerValue, accessibleQuestionnaires,
      toggleView, formatDate, questionnaireCreateUrl, control
    }
  }
}
</script>

<style scoped>
@import '../../css/questionnaires.css';
</style>
