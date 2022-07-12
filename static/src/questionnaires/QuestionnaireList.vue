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
          <label v-for="ctrl in accessibleControls"
                :key="ctrl.id"
                class="custom-control custom-checkbox">
            <input type="checkbox" class="custom-control-input" :value="ctrl.id" v-model="checkedCtrls">
            <span class="custom-control-label">{{ ctrl.depositing_organization }} - {{ ctrl.title }} ({{ ctrl.reference_code }})</span>
          </label>
        </div>
      </form>
    </confirm-modal>
    <div class="card-status card-status-top bg-blue"></div>
    <div class="card-header" style="display: block; padding: 1rem">
      <div class="float-right" v-if="hasAnyAnswer">
        <button @click="toggleView()" style="font-size:smaller" class="card-title btn btn-primary ml-4" :title="isList ? 'Voir les documents' : 'Voir les questionnaires'">{{isList ? 'Voir les documents' : 'Voir les questionnaires'}}</button>
      </div>
      <h2 class="card-title">
        <i class="fe fe-folder mr-2" :class="{'fe-list':isList}" aria-hidden="true"></i>
        <span>{{isList ? 'Questionnaires' : 'Documents'}}</span>
      </h2>
    </div>

    <div v-if="currentView === 'questions'">
      <div
        v-if="accessibleQuestionnaires.length === 0"
        class="alert alert-icon alert-secondary m-2"
      >
        <i class="fe fe-info mr-2" aria-hidden="true"></i>
        Il n'y a pas encore de questionnaire pour cet espace de dépôt.
      </div>
      <table v-else class="table card-table table-vcenter">
        <thead>
          <tr>
            <th v-if="user.is_inspector">
              Statut
              <help-tooltip
                text="Un questionnaire est d'abord en Brouillon : il est modifiable et
                                  l'organisme interrogé ne le voit pas. Puis il est Publié : il
                                  n'est plus modifiable et l'organisme interrogé le voit."
              >
              </help-tooltip>
            </th>
            <th>Titre</th>
            <th>Date de réponse</th>
            <th v-if="user.is_inspector">Rédacteur</th>
            <td class="border-bottom"></td>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="questionnaire in accessibleQuestionnaires"
            :key="'questionnaire-' + questionnaire.id"
          >
            <td class="tag-column" v-if="user.is_inspector">
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
            <td v-if="user.is_inspector" class="editor-column">
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
              <template v-if="!user.is_inspector">
                <div v-if="questionnaire.has_replies && !questionnaire.is_replied" class="text-right">
                   <div class="btn-group">
                      <a class="btn btn-secondary"
                        :href="questionnaireDetailUrl(questionnaire.id)"
                        title="Déposer et consulter vos réponses">
                        <i class="fe fe-eye" aria-hidden="true"></i>
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
                        <i class="fe fe-check" aria-hidden="true"></i>
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
                    <i class="fe fe-eye" aria-hidden="true"></i>
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
                        <i class="fe fe-edit" aria-hidden="true"></i>
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
                        <i class="fe fe-trash-2" aria-hidden="true"></i>
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
                      <i class="fe fe-eye" aria-hidden="true"></i>
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
                      <i class="fe fe-eye" aria-hidden="true"></i>
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
                        <i class="fe fe-copy" aria-hidden="true"></i>
                        Dupliquer
                      </button>
                      <button class="dropdown-item"
                              type="button"
                              @click="exportControl(questionnaire.id)"
                      >
                        <i class="fas fa-file-export mr-2" aria-hidden="true"></i>
                        Exporter (.zip)
                      </button>
                      <button
                        v-if="questionnaire.is_replied && !questionnaire.is_finalized"
                        class="dropdown-item text-success"
                        type="button"
                        @click="markQuestionnaireAsFinalized(questionnaire.id)"
                      >
                        <i class="fe fe-check" aria-hidden="true"></i>
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
      v-if="user.is_inspector"
      class="card-footer flex-row justify-content-end"
    >
      <a :href="questionnaireCreateUrl" class="btn btn-primary">
        <i class="fe fe-plus" aria-hidden="true"></i>
        Ajouter un questionnaire
      </a>
    </div>
  </div>
</template>

<script>
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
  props: ['control', 'user'],
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
      if (this.user.is_inspector) {
        return this.control.questionnaires
      }
      return this.control.questionnaires.filter(
        (questionnaire) => !questionnaire.is_draft,
      )
    },
    questionnaireCreateUrl() {
      return backendUrls['questionnaire-create'](this.control.id)
    },
    hasAnyAnswer() {
      let questionnaires = this.accessibleQuestionnaires.filter(aq => aq.has_replies);
      return (questionnaires.length > 0);
    }
  },
  methods: {
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
    toggleView(){
      if (this.isList) {
        this.currentView = 'tree';
      } else {
        this.currentView = 'questions';
      }
      this.isList = !this.isList;
    },
    toggleView(){
      if (this.isList) {
        this.currentView = 'tree';
      } else {
        this.currentView = 'questions';
      }
      this.isList = !this.isList;
    },
    cloneQuestionnaire() {
      let self = this;
      const getCreateMethod = () => axios.post.bind(this, backendUrls.questionnaire())
      const getUpdateMethod = (qId) => axios.put.bind(this, backendUrls.questionnaire(qId))

      if (this.checkedCtrls.length) {
        const curQ = this.control.questionnaires.find(q => q.id === this.questionnaireId)
        const destCtrls = this.controls.filter(ctrl => this.checkedCtrls.includes(ctrl.id))

        destCtrls.forEach(ctrl => {
          const themes = curQ.themes.map(t => {
            const qq = t.questions.map(q => {
              return { description: q.description }
            })
            return { title: t.title, questions: qq }
          })

          let newQ = { ...curQ, control: ctrl.id, is_draft: true, id: null, themes: [] }
          getCreateMethod()(newQ).then(response => {
            const qId = response.data.id
            newQ = { ...newQ, themes: themes }

            getUpdateMethod(qId)(newQ).then(response => {
              const updatedQ = response.data

              // Update questionnaires list render when duplicated
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
      this.loaderActive = true;

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
        this.loaderActive = false;
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
              this.loaderActive = false;
              saveAs(content, zipFilename)
            })
          }
        })
      })

    },
  },
})
</script>

<style scoped>
.tag-column {
  max-width: 7em;
}

.editor-column {
  min-width: 9em;
}

.editor-date {
  display: block;
}

.end-date-column {
  min-width: 9em;
}

.action-column {
  min-width: 10em;
}
</style>
