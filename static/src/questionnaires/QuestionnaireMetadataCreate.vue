<template>
  <div>
    <div class="card">
      <div class="card-header">
        <h2 class="card-title">
          <span data-v-d81dfb="" class="number"></span>
          <span class="sr-only">En cours de consultation</span>
          Etape 1 : Renseigner l'introduction
        </h2>
      </div>
      <div class="card-body pb-6">
        <form ref="form">
          <div class="form-group">
            <label class="form-label" id="questionnaireTitle" for="questionnaire_title">
              Quel titre souhaitez vous donner au questionnaire n°{{ questionnaireNumbering }} ?
              <span class="form-required">*</span>
            </label>
            <span class="text-muted" id="questionnaireTitleHelp">
              Exemple :
              <strong>"Présentation générale"</strong>
              ou
              <strong>"Suite à la réunion du ..."</strong>. 255 caractères maximum.
            </span>
            <input id="questionnaire_title"
                   type="text"
                   aria-labelledby="questionnaireTitle"
                   aria-describedby="questionnaireTitleHelp"
                   class="form-control"
                   v-model="title"
                   maxlength="255"
                   required>
          </div>
          <div class="form-group">
            <label class="form-label" id="questionnaireDescription" for="questionnaire_description">
              Vous pouvez modifier le texte d'introduction du questionnaire
              n°{{ questionnaireNumbering }}, si vous le souhaitez :
            </label>
            <textarea id="questionnaire_description"
                      class="form-control"
                      aria-labelledby="questionnaireDescription"
                      placeholder="Si nécessaire, décrivez votre questionnaire ici"
                      rows="6"
                      v-bind:class="{ 'state-invalid': errors.description }"
                      v-model="description">
            </textarea>
            <p class="text-muted pl-2" v-if="errors.description">
              <span class="fa fa-warning" aria-hidden="true"></span> {{ errors.description.join(' / ')}}
            </p>
          </div>
          <div class="form-group">
            <label class="form-label" id="questionnaireEndDate" for="questionnaire_enddate">
              Vous pouvez indiquer la date limite de réponse :
            </label>
            <datepicker id="questionnaire_enddate"
                        class="blue"
                        aria-labelledby="questionnaireEndDate"
                        v-model="end_date"
                        :language="fr"
                        :typeable="true"
                        :use-utc="true"
                        :placeholder="placeholder"
                        :format="format"
                        :monday-first="true">
            </datepicker>
          </div>
          <div class="form-group">
            <questionnaire-file-upload :questionnaire="questionnaire"></questionnaire-file-upload>
            <questionnaire-file-list :files="questionnaire.questionnaire_files" :with-delete="true">
            </questionnaire-file-list>
          </div>
        </form>
        <a class="wizard-step-graphics">
          <span class="sr-only">Étape validée</span>
        </a>
      </div>
    </div>
  </div>
</template>


<script>
import { defineComponent, computed, ref } from 'vue'
import { useStore } from 'vuex'
import Datepicker from 'vue3-datepicker'
import fr from '../utils/vuejs-datepicker-locale-fr'
import reportValidity from 'report-validity'
import QuestionnaireFileUpload from './QuestionnaireFileUpload'
import QuestionnaireFileList from './QuestionnaireFileList'

// Texte par défaut
const DESCRIPTION_DEFAULT = 'À l’occasion de cette procédure, \
nous vous demandons de nous transmettre des renseignements et des justifications \
sur les points énumérés dans ce questionnaire.\nVous voudrez bien nous faire \
parvenir au fur et à mesure votre réponse. \
\nNous restons à votre disposition ainsi qu’à celle de vos \
services pour toute information complémentaire qu’appellerait ce questionnaire.'

export default defineComponent({
  name: 'QuestionnaireMetadataCreate',
  props: {
    questionnaireNumbering: Number,
    questionnaire: Object,
  },
  setup(props) {
    const store = useStore()
    const formRef = ref(null)

    // Accès direct aux champs du store
    const description = computed({
      get: () => store.state.currentQuestionnaire.description,
      set: (value) => store.commit('updateCurrentQuestionnaireField', { field: 'description', value })
    })

    const end_date = computed({
      get: () => store.state.currentQuestionnaire.end_date,
      set: (value) => store.commit('updateCurrentQuestionnaireField', { field: 'end_date', value })
    })

    const title = computed({
      get: () => store.state.currentQuestionnaire.title,
      set: (value) => store.commit('updateCurrentQuestionnaireField', { field: 'title', value })
    })

    const errors = ref([])
    const frLocale = fr
    const format = 'yyyy-MM-dd'
    const placeholder = 'yyyy-mm-dd'

    const validateForm = () => {
      return formRef.value ? reportValidity(formRef.value) : true
    }

    return {
      description,
      end_date,
      title,
      errors,
      frLocale,
      format,
      placeholder,
      formRef,
      validateForm,
    }
  },
  components: {
    Datepicker,
    QuestionnaireFileUpload,
    QuestionnaireFileList,
  },
})

QuestionnaireMetadataCreate.DESCRIPTION_DEFAULT = DESCRIPTION_DEFAULT
</script>
