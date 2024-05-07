<template>
  <div class="card">
    <confirm-modal
      ref="modal"
      cancel-button="Annuler"
      confirm-button="Dupliquer le questionnaire"
      title="Dupliquer un questionnaire"
      @confirm="cloneQuestionnaire"
    >
      <info-bar>
        <p>Veuillez sélectionner les espaces de dépôt vers lesquels vous souhaitez dupliquer ce questionnaire.</p>
      </info-bar>
      <form>
        <div class="form-group mb-6">
          <label v-for="ctrl in controls"
                :for="ctrl.id"
                :key="ctrl.id"
                class="custom-control custom-checkbox">
            <input :id="ctrl.id" type="checkbox" class="custom-control-input" :value="ctrl.id" v-model="checkedCtrls">
            <span class="custom-control-label">{{ ctrl.depositing_organization }} - {{ ctrl.title }} ({{ ctrl.reference_code }})</span>
          </label>
        </div>
      </form>
    </confirm-modal>
    <div class="card-status card-status-top bg-blue"></div>
    <div class="card-header custom-card-header">
      <div class="float-right" v-if="hasAnyAnswerValue">
        <button @click="toggleView()" class="card-title btn btn-primary ml-4 view-button" :title="isList ? 'Voir les documents' : 'Voir les questionnaires'">{{isList ? 'Voir les documents' : 'Voir les questionnaires'}}</button>
      </div>
      <h2 class="card-title">
        <span class="fe fe-folder mr-2" :class="{'fe-list':isList}" aria-hidden="true"></span>
        <span>{{isList ? 'Questionnaires' : 'Documents'}}</span>
      </h2>
    </div>

    <div v-if="currentView === 'questions'">
      <div
        v-if="accessibleQuestionnaires.length === 0"
        class="alert alert-icon alert-secondary m-2"
        role="status"
      >
        <span class="fe fe-info mr-2" aria-hidden="true"></span>
        Il n'y a pas encore de questionnaire pour cet espace de dépôt.
      </div>
      <table v-else class="table card-table table-vcenter">
        <caption class="sr-only">Questionnaires</caption>
        <thead>
          <tr>
            <th v-if="accessType === 'demandeur'" scope="col">
              Statut
              <help-tooltip
                text="Brouillon : modifiable, l'organisme interrogé ne le voit pas<br />
Publié : non modifiable, l'organisme interrogé le voit<br />
En cours : l'organisme interrogé a commencé à déposer les réponses<br />
Répondu : l'organisme interrogé a fini de répondre au questionnaire<br />
Finalisé : l'instruction des pièces déposées est achevée">
              </help-tooltip>
            </th>
            <th scope="col">Titre</th>
            <th scope="col">Date de réponse</th>
            <th v-if="accessType === 'demandeur'" scope="col">Rédacteur</th>
            <td class="border-bottom"></td>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="questionnaire in accessibleQuestionnaires"
            :key="'questionnaire-' + questionnaire.id"
          >
            <td class="tag-column" v-if="accessType === 'demandeur'">
              <div v-if="questionnaire.is_draft">
                <div class="tag tag-azure round-tag font-italic">Brouillon</div>
              </div>
              <div v-else-if="questionnaire.has_replies && !questionnaire.is_replied">
                <div class="tag tag-yellow round-tag font-italic">En cours</div>
              </div>
              <div v-else-if="questionnaire.is_replied && !questionnaire.is_finalized">
                <div class="tag tag-orange round-tag font-italic">Répondu</div>
              </div>
              <div v-else-if="questionnaire.is_finalized">
                <div class="tag tag-purple round-tag font-italic">Finalisé</div>
              </div>
              <div v-else>
                <div class="tag tag-green round-tag font-italic">Publié</div>
              </div>
            </td>
            <td>
              <div>Questionnaire {{ questionnaire.numbering }}</div>
              <div>{{ questionnaire.title }}</div>
            </td>
            <td class="end-date-column">
              <div v-if="questionnaire.end_date">
                <small>
                  {{ questionnaire.end_date | DateFormat }}
                </small>
              </div>
            </td>
            <td v-if="accessType === 'demandeur'" class="editor-column">
              <div v-if="questionnaire.is_draft && questionnaire.editor">
                <help-tooltip
                  v-if="questionnaire.editor.id !== user.id"
                  text="Cette personne dispose des droits pour modifier ce
                                    questionnaire. Vous pourrez modifier ce questionnaire en
                                    cliquant sur 'Consulter', puis 'Obtenir les droits de
                                    rédaction'."
                  icon-class="fe fe-lock"
                >
                </help-tooltip>
                <small>
                  {{ questionnaire.editor.first_name }}
                  {{ questionnaire.editor.last_name }}
                  <span v-if="questionnaire.modified_date" class="text-muted editor-date">
                    {{ questionnaire.modified_date }} à
                    {{ questionnaire.modified_time }}
                  </span>
                </small>
              </div>
            </td>
            <td class="w-1 action-column">
              <template v-if="accessType !== 'demandeur'">
                <div v-if="questionnaire.has_replies && !questionnaire.is_replied" class="text-right">
                   <div class="btn-group">
                      <a class="btn btn-secondary"
                        :href="questionnaireDetailUrl(questionnaire.id)"
                        title="Déposer et consulter vos réponses">
                        <span class="fe fe-eye" aria-hidden="true"></span>
                        Répondre
                      </a>
                       <button
                      type="button"
                      class="btn btn-secondary dropdown-toggle dropdown-toggle-split"
                      data-toggle="dropdown"
                      aria-haspopup="true"
                      aria-expanded="false"
                    >
                      <span class="sr-only">Menu d'actions</span>
                    </button>
                    <div class="dropdown-menu dropdown-menu-right">
                      <button
                        class="dropdown-item text-success"
                        type="button"
                        @click="markQuestionnaireAsReplied(questionnaire.id)"
                      >
                        <span class="fe fe-check" aria-hidden="true"></span>
                        Marquer comme répondu
                      </button>
                    </div>
                  </div>
                </div>
                <div v-else class="text-right">
                  <a
                    :href="questionnaireDetailUrl(questionnaire.id)"
                    class="btn btn-primary ml-2"
                    title="Déposer et consulter vos réponses"
                  >
                    <span class="fe fe-eye" aria-hidden="true"></span>
                    Répondre
                  </a>
                </div>
              </template>
              <template v-else>
                <template
                  v-if="
                    questionnaire.is_draft &&
                    !!questionnaire.editor &&
                    questionnaire.editor.id === user.id
                  "
                >
                  <div class="text-right">
                    <div class="btn-group">
                      <a class="btn btn-secondary"
                        :href="questionnaireEditUrl(questionnaire.id)"
                        title="Modifier le brouillon de questionnaire">
                        <span class="fe fe-edit" aria-hidden="true"></span>
                        Modifier
                      </a>
                       <button
                      type="button"
                      class="btn btn-secondary dropdown-toggle dropdown-toggle-split"
                      data-toggle="dropdown"
                      aria-haspopup="true"
                      aria-expanded="false"
                    >
                      <span class="sr-only">Menu d'actions</span>
                    </button>
                    <div class="dropdown-menu dropdown-menu-right">
                      <button
                        class="dropdown-item text-danger"
                        type="button"
                        @click="startQuestionnaireDeleteFlow(questionnaire.id)"
                      >
                        <span class="fe fe-trash-2" aria-hidden="true"></span>
                        Supprimer
                      </button>
                    </div>
                  </div>
                </template>
                <template v-else-if="questionnaire.is_draft &&
                                    questionnaire.editor.id !== user.id"
                >
                  <div class="text-right">
                    <a :href="questionnaireDetailUrl(questionnaire.id)"
                      class="btn btn-primary ml-2"
                      title="Voir le brouillon de questionnaire"
                    >
                      <span class="fe fe-eye" aria-hidden="true"></span>
                      Consulter
                    </a>
                  </div>
                </template>
                <template v-else>
                  <div class="text-right">
                    <div class="btn-group">
                    <a
                      :href="questionnaireDetailUrl(questionnaire.id)"
                      title="Voir le questionnaire publié"
                      class="btn btn-secondary"
                    >
                      <span class="fe fe-eye" aria-hidden="true"></span>
                      Consulter
                    </a>
                    <button
                      type="button"
                      class="btn btn-secondary dropdown-toggle dropdown-toggle-split"
                      data-toggle="dropdown"
                      aria-haspopup="true"
                      aria-expanded="false"
                    >
                      <span class="sr-only">Menu d'actions</span>
                    </button>
                    <div class="dropdown-menu dropdown-menu-right">
                      <button
                        class="dropdown-item"
                        type="button"
                        @click="showModal(questionnaire.id)"
                      >
                        <span class="fe fe-copy" aria-hidden="true"></span>
                        Dupliquer
                      </button>
                      <button class="dropdown-item"
                              type="button"
                              @click="exportControl(questionnaire.id)"
                      >
                        <span class="fas fa-file-export mr-2" aria-hidden="true"></span>
                        Exporter (.zip)
                      </button>
                      <button
                        v-if="questionnaire.is_replied && !questionnaire.is_finalized"
                        class="dropdown-item text-success"
                        type="button"
                        @click="markQuestionnaireAsFinalized(questionnaire.id)"
                      >
                        <span class="fe fe-check" aria-hidden="true"></span>
                        Marquer comme finalisé
                      </button>
                    </div>
                  </div>
                </template>
              </template>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-if="currentView === 'tree'">
      <questionnaire-tree-view :control="control"></questionnaire-tree-view>
    </div>

    <div
      v-if="accessType === 'demandeur'"
      class="card-footer flex-row justify-content-end"
    >
      <a :href="questionnaireCreateUrl" class="btn btn-primary">
        <span class="fe fe-plus" aria-hidden="true"></span>
        Ajouter un questionnaire
      </a>
    </div>
  </div>
</template>

<script>
import '../../css/questionnaires.css'
import axios from 'axios'
import backendUrls from '../utils/backend'
import DateFormat from '../utils/DateFormat.js'
import HelpTooltip from '../utils/HelpTooltip'
import InfoBar from '../utils/InfoBar'
import ConfirmModal from '../utils/ConfirmModal'
import Vue from 'vue'
import Vuex, { mapState } from 'vuex'
import QuestionnaireTreeView from '../questionnaires/QuestionnaireTreeView'

import JSZip from 'jszip'
import JSZipUtils from 'jszip-utils'
import { saveAs } from 'file-saver'

Vue.use(Vuex)

export default Vue.extend({
  props: ['control', 'user', 'accessType'],
  filters: {
    DateFormat,
  },
  components: {
    HelpTooltip,
    InfoBar,
    ConfirmModal,
    QuestionnaireTreeView,
  },
  data: function() {
    return {
      questionnaireId: null,
      checkedCtrls: [],
      currentView: 'questions',
      isList: true,
      currentQuestionnaireThemes: [],
      hasAnyAnswerValue: false,
    }
  },
  computed: {
    ...mapState({
      controls: 'controls',
      
    }),
    accessibleControls() {
      return this.controls
    },
    accessibleQuestionnaires() {
      if (this.accessType === 'demandeur') {
        return this.control.questionnaires
      }
      return this.control.questionnaires.filter(
        (questionnaire) => !questionnaire.is_draft,
      )
    },
    questionnaireCreateUrl() {
      return backendUrls['questionnaire-create'](this.control.id)
    },
    
  },
  mounted() {
    this.checkAnyAnswer();
  },
  methods: {
    async checkAnyAnswer() {
          
    try {
        const resp = await axios.get(backendUrls.getQuestionnaireAndThemesByCtlId(this.control.id));
        this.control = resp.data.filter(obj => obj.id === this.control.id)[0];
        let questionnaires = this.accessibleQuestionnaires.filter(aq => aq.has_replies);
        this.hasAnyAnswerValue = questionnaires.length > 0;
      } catch (error) {
        console.error('Erreur lors de la requête HTTP :', error);
        this.hasAnyAnswerValue = false; 
      }
    },
    questionnaireDetailUrl(questionnaireId) {
      return backendUrls['questionnaire-detail'](questionnaireId)
    },
    questionnaireEditUrl(questionnaireId) {
      return backendUrls['questionnaire-edit'](questionnaireId)
    },
    startQuestionnaireDeleteFlow(questionnaireId) {
      let self = this;
      const getUpdateMethod = (qId) => axios.put.bind(this, backendUrls.questionnaire(qId))
      const curQ = this.control.questionnaires.find(q => q.id === questionnaireId)
      const newQ = { ...curQ, control: null }

      getUpdateMethod(questionnaireId)(newQ).then(() => {
        self.$root.$emit('questionnaire-created')
      })
    },
    exportUrl(questionnaire) {
      return backendUrls['questionnaire-export'](questionnaire.id)
    },
    showModal(qId) {
      this.questionnaireId = qId
      $(this.$refs.modal.$el).modal('show')
    },
    markQuestionnaireAsReplied(qId) {
      const getUpdateMethod = (qId) => axios.put.bind(this, backendUrls.questionnaire(qId))
      const curQ = this.control.questionnaires.find(q => q.id === qId)
      const newQ = { ...curQ, is_replied: true }
      getUpdateMethod(qId)(newQ).then(() => {
        window.location.reload();
      })
    },
    markQuestionnaireAsFinalized(qId) {
      const getUpdateMethod = (qId) => axios.put.bind(this, backendUrls.questionnaire(qId))
      const curQ = this.control.questionnaires.find(q => q.id === qId)
      const newQ = { ...curQ, is_finalized: true }
      getUpdateMethod(qId)(newQ).then(() => {
        window.location.reload();
      })
    },
    toggleView() {
      if (this.isList) {
        this.currentView = 'tree';
      } else {
        this.currentView = 'questions';
      }
      this.isList = !this.isList;
    },
    async cloneQuestionnaire() {
      let self = this
      const getCreateMethod = () => axios.post.bind(this, backendUrls.questionnaire())
      const getUpdateMethod = (qId) => axios.put.bind(this, backendUrls.questionnaire(qId))

      if (this.checkedCtrls.length) {

        const resp = await axios.get(backendUrls.getQuestionnaireAndThemesByCtlId(this.control.id))
        this.control = resp.data.filter(obj => obj.id === this.control.id)[0]
        const curQ = this.control.questionnaires.find(q => q.id === this.questionnaireId)
        const destCtrls = this.controls.filter(ctrl => this.checkedCtrls.includes(ctrl.id))

        destCtrls.forEach(ctrl => {
          const themes = curQ.themes.map(t => {
            const qq = t.questions.map(q => {
              return { description: q.description }
            })
            return { title: t.title, questions: qq }
          })

          let newQ = { ...curQ, control: ctrl.id, questionnaire_files:curQ.questionnaire_files, is_draft: true, is_replied: false, has_replies:false, is_finalized: false, id: null, themes: [] }
          
          getCreateMethod()(newQ).then(response => {
            const qId = response.data.id
            newQ = { ...newQ, id: qId, questionnaire_files:curQ.questionnaire_files, themes: themes }
            curQ.questionnaire_files.forEach(qf => {
                    axios.get(qf.url, { responseType: 'blob' }).then(response => {
                      const formData = new FormData()
                      formData.append('file', response.data, qf.basename)
                      formData.append('questionnaire', qId)

                      axios.post(backendUrls.piecejointe(), formData, {
                        headers: {
                          'Content-Type': 'multipart/form-data',
                        },
                      })
                    })
              })
            
            getUpdateMethod(qId)(newQ).then(response => {
              const updatedQ = response.data
              self.$root.$emit('questionnaire-created')
              curQ.themes.forEach(t => {
                t.questions.forEach(q => {
                  const qId = updatedQ.themes.find(updatedT => updatedT.order === t.order)
                    .questions.find(updatedQ => updatedQ.order === q.order).id
                  
                    q.question_files.forEach(qf => {
                    axios.get(qf.url, { responseType: 'blob' }).then(response => {
                      const formData = new FormData()
                      formData.append('file', response.data, qf.basename)
                      formData.append('question', qId)
                      
                      axios.post(backendUrls.annexe(), formData, {
                        headers: {
                          'Content-Type': 'multipart/form-data',
                        },
                      })
                    })
                  })
                })
              })
            })
          })
              
        });
      }
    },
   
    exportControl(questionnaireId) {
      this.$parent.$children[0].loaderActive = true;

      const formatFilename = (file) => {
        const questionnaireNb = String(file.questionnaireNb).padStart(2, '0')
        const questionnaireId = `Q${questionnaireNb}`;
        let themeId = '';
        let filename = ''
        if (file.category == 'question_file') {
          themeId = 'ANNEXES-AUX-QUESTIONS';
          filename = `Q${questionnaireNb}-${file.basename}`;
        } else if (file.is_deleted) {
          themeId = 'CORBEILLE';
          filename = `Q${questionnaireNb}-${file.basename}`;
        } else {
          themeId = 'T'+String(file.themeId + 1).padStart(2, '0');
          const questionId = String(file.questionId + 1).padStart(2, '0');
          filename = `Q${questionnaireNb}-${themeId}-${questionId}-${file.basename}`;
        }
        return { questionnaireId, themeId, filename };
      }

      let files = this.accessibleQuestionnaires
        .filter(aq => questionnaireId === aq.id)
        .flatMap(fq => {
          if (fq.themes) {
            return fq.themes.flatMap(t => {
              if (t.questions) {
                return t.questions.flatMap(q => {
                  return q.response_files.flatMap(rf => {
                    if (rf) {
                      return {
                        questionnaireNb: fq.numbering,
                        themeId: t.order,
                        questionId: q.order,
                        category: 'response_file',
                        basename: rf.basename,
                        url: rf.url,
                        is_deleted: rf.is_deleted,
                      }
                    }
                  })
                })
              }
            })
          }
        })
      files.push.apply(
        files,
        this.accessibleQuestionnaires
        .filter(aq => questionnaireId == aq.id)
        .flatMap(fq => {
          if (fq.themes) {
            return fq.themes.flatMap(t => {
              if (t.questions) {
                return t.questions.flatMap(q => {
                  return q.question_files.flatMap(qf => {
                    if (qf) {
                      return {
                        questionnaireNb: fq.numbering,
                        themeId: t.order,
                        questionId: q.order,
                        category: 'question_file',
                        basename: qf.basename,
                        url: qf.url,
                        is_deleted: qf.is_deleted,
                      }
                    }
                  })
                })
              }
            })
          }
        })
      );

      const zipFilename = this.control.reference_code + '.zip'
      const zip = new JSZip()
      let cnt = 0

      if (files.length==0) {
          this.$parent.$children[0].loaderActive = false;
      }

      files.map(file => {
        const url = window.location.origin + file.url;
        JSZipUtils.getBinaryContent(url, (err, data) => {
          if (err) throw err;
          const formatted = formatFilename(file);
          zip.folder(formatted.questionnaireId)
            .folder(formatted.themeId)
            .file(formatted.filename, data, { binary: true });

          cnt++;
          if (cnt === files.length) {
            zip.generateAsync({ type: 'blob' }).then((content) => {
              this.$parent.$children[0].loaderActive = false;
              saveAs(content, zipFilename)
            })
          }
        })
      })

    },
  },
})
</script>
