<template>
    <div id="app" class="card">
        <confirm-modal
          ref="modal"
          cancel-button="Annuler"
          confirm-button="Dupliquer le questionnaire"
          title="Dupliquer un questionnaire"
          @confirm="cloneQuestionnaire"
        >
          <info-bar>
            Veuillez sélectionner les espaces de dépôt vers lesquels vous souhaitez dupliquer ce questionnaire.
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
        <div class="card">
          <span>
            <span class="mr-8"> Filtrer par répondant
              <select v-model="filter" class="col-xs-2">
                <option></option>
                <option v-for="option in repondantsListe" :key="option">
                  {{ option.first_name + ' ' + option.last_name }}
                </option>
              </select>
            </span>
            <span> Filtrer par date de dépôt de
              <input placeholder="Date de début">
              à
              <input placeholder="Date de fin">
            </span>
          </span>
        </div>
        <vue-ads-table
            :columns="columns"
            :rows="treeViewElements"
            :filter="filter"
            @filter-change="filterChanged"
        >
            <!-- Will be applied on the name column for the rows with an _id of tiger -->
            <template slot="name" slot-scope="props">{{ props.row.name }}</template>
            <template slot="dateDepot" slot-scope="props">{{ props.row.dateDepot }}</template>
            <template slot="repondant" slot-scope="props">{{ props.row.repondant }}</template>
            <template slot="action_questionnaire" slot-scope="props">
                <div class="btn-group">
                    <a
                      :href="questionnaireDetailUrl(props.row.id)"
                      title="Voir le questionnaire publié"
                      class="btn btn-secondary"
                    >
                      <i class="fe fe-eye"></i>
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
                        @click="showModal(props.row.id)"
                      >
                        <i class="fe fe-copy"></i>
                        Dupliquer
                      </button>
                      <button class="dropdown-item"
                              type="button"
                              @click="exportControl(props.row.id, props.row._id)"
                      >
                        <i class="fas fa-file-export mr-2"></i>
                        Exporter
                      </button>
                    </div>
                </div>
            </template>
            <template slot="action_theme" slot-scope="props">
                <a
                    class="btn btn-secondary"
                    @click="exportControl(props.row.id, props.row._id)"
                >
                    <i class="fas fa-file-export"></i>
                    Exporter
                </a>
            </template>
            <template slot="action_question" slot-scope="props">
                <a
                    class="btn btn-secondary"
                    @click="exportControl(props.row.id, props.row._id)"
                >
                    <i class="fas fa-file-export"></i>
                    Exporter
                </a>
            </template>
            <template slot="action_file" slot-scope="props">
                <a
                    class="btn btn-secondary"
                    @click="exportControl(props.row.id, props.row._id)"
                >
                    <i class="fas fa-file-export"></i>
                    Exporter
                </a>
            </template>
            <template slot="no-rows">Pas de résultats</template>
            <template slot="toggle-children-icon" slot-scope="props"></template>
        </vue-ads-table>
    </div>
</template>

<script>
import axios from 'axios';
import backendUrls from '../utils/backend';

import '../../../node_modules/@fortawesome/fontawesome-free/css/all.min.css';
import '../../../node_modules/vue-ads-table-tree/dist/vue-ads-table-tree.css';

import InfoBar from '../utils/InfoBar'
import ConfirmModal from '../utils/ConfirmModal'

import Vue from 'vue';
import { mapState } from 'vuex'
import { VueAdsTable } from 'vue-ads-table-tree';

import JSZip from 'jszip'
import JSZipUtils from 'jszip-utils'
import { saveAs } from 'file-saver'

export default Vue.extend({
    props: {
        control: {type: Object, default: () => ({})}
    },
    components: {
        InfoBar,
        ConfirmModal,
        VueAdsTable,
    },

    data () {
        let columns = [
            {
                property: 'name',
                title: 'Nom du document',
            },
            {
                property: 'dateDepot',
                title: 'Date de dépot',
                filterable: true,
            },
            {
                property: 'repondant',
                title: 'Répondant',
                filterable: true,
            },
            {
                property: 'action',
                title: 'Action',
            },
        ];

        let classes = {
            group: {
                'vue-ads-font-bold': true,
                'vue-ads-border-b': true,
                'vue-ads-italic': true,
            },
            '0/all': {
                'vue-ads-py-3': true,
                'vue-ads-px-2': true,
            },
            'even/': {
                'vue-ads-bg-blue-lighter': true,
            },
            'odd/': {
                'vue-ads-bg-blue-lightest': true,
            },
            '0/': {
                'vue-ads-bg-blue-lighter': false,
                'vue-ads-bg-blue-dark': true,
                'vue-ads-text-white': false,
                'vue-ads-font-bold': true,
            },
            '1_/': {
                'hover:vue-ads-bg-red-lighter': true,
            },
            '1_/0': {
                'leftAlign': true
            }
        };

        return {
            columns,
            classes,
            filter: '',
            checkedCtrls: [],
            checkedElements: [],
            repondantsListe: [],
        };
    },

    computed: {
        ...mapState({
          controls: 'controls',
        }),
        accessibleControls() {
          return this.controls
        },
        accessibleQuestionnaires() {
          return this.control.questionnaires.filter(q => !q.is_draft)
        },
        treeViewElements() {

            return this.accessibleQuestionnaires.map(element => {
                const objQuestionnaire = this.getTreeViewLevel(element);

                if (
                    Object.prototype.hasOwnProperty.call(element, 'themes') &&
                    element.themes.length
                ) {

                    objQuestionnaire._children = element.themes.map(theme => {
                        const objTheme = this.getTreeViewLevel(theme, element.id);

                        if (
                            Object.prototype.hasOwnProperty.call(theme, 'questions') &&
                            theme.questions.length
                        ) {
                            objTheme._children = theme.questions.map(question => {
                                const objQuestion = this.getTreeViewLevel(question, element.id, theme.id);

                                if (
                                    Object.prototype.hasOwnProperty.call(question, 'response_files') &&
                                    question.response_files.length
                                ) {
                                    objQuestion._children = question.response_files
                                                                    .filter(responseFile => responseFile.is_deleted === false)
                                                                    .map(responseFile => this.getTreeViewLevel(responseFile, element.id, theme.id, question.id));
                                    objQuestion._showChildren = true;
                                    objQuestion._selectable = true;
                                } else {
                                    objQuestion._showChildren = false;
                                }

                                return objQuestion;
                            });
                        }

                        return objTheme;
                    });
                }

                const objAnnexes = this.getTreeViewLevel(null, null, null, null, true);
                const objCorbeille = this.getTreeViewLevel(null, null, null, null, false, true);

                objAnnexes._children = this.accessibleQuestionnaires
                  .filter(aq => aq.id === element.id)
                  .flatMap(fq => {
                    if (fq.themes) {
                      return fq.themes.flatMap(t => {
                        if (t.questions) {
                          return t.questions.flatMap(q => {
                            return q.question_files.flatMap(qf => {
                              if (qf) {
                                return this.getTreeViewLevel(qf, null, null, null, false, false, true);
                              }
                            })
                          })
                        }
                      })
                    }
                  })

                objCorbeille._children = this.accessibleQuestionnaires
                  .filter(aq => aq.id === element.id)
                  .flatMap(fq => {
                    if (fq.themes) {
                      return fq.themes.flatMap(t => {
                        if (t.questions) {
                          return t.questions.flatMap(q => {
                            return q.response_files
                              .filter(rf => rf.is_deleted === true)
                              .flatMap(rf => {
                                if (rf) {
                                  return this.getTreeViewLevel(rf, null, null, null, false, false, false, true);
                                }
                            })
                          })
                        }
                      })
                    }
                  })

                if (!objAnnexes._children.length) {
                  objAnnexes._showChildren = false;
                }

                if (!objCorbeille._children.length) {
                  objCorbeille._showChildren = false;
                }

                objQuestionnaire._children.unshift(objAnnexes, objCorbeille);

                return objQuestionnaire;
            });
        },
    },
    methods: {
        filterChanged (filter) {
            this.filter = filter;
        },
        getUsers() {
          axios.get(backendUrls.getUsersInControl(this.control.id))
            .then((response) => {
              this.repondantsListe = response.data.filter(item => {
                return item.profile_type === 'audited'
              });
            })
        },
        /**
         * get formatted item for treeview plugin
         */
        getTreeViewLevel(item, questionnaireId = null, themeId = null, questionId = null, isAnnexe = false, isCorbeille = false, isFichierAnnexe = false, isFichierCorbeille = false) {
            const objectTreeView = {
                name: '',
                dateDepot: '',
                repondant: '',
                _showChildren: true,
                _children: [],
                _id: '',
                id: '',
                url: ''
            };

            if (isAnnexe) { // Annexes
                objectTreeView.name = 'Annexes';
                objectTreeView._children = [];
                objectTreeView._id = 'annexes';
            } else if (isCorbeille) { // Corbeille
                objectTreeView.name = 'Corbeille';
                objectTreeView._children = [];
                objectTreeView._id = 'corbeille';
            } else if (isFichierAnnexe) { // Fichier annexe
                objectTreeView.name = item.basename;
                objectTreeView.url = item.url;
                objectTreeView._showChildren = false;
            } else if (isFichierCorbeille) { // Fichier corbeille
                objectTreeView.name = item.basename;
                objectTreeView.dateDepot = item.created;
                objectTreeView.repondant = item.author.first_name + ' ' + item.author.last_name;
                objectTreeView.url = item.url;
                objectTreeView._showChildren = false;
            } else if (questionId != null) { // Response_file
                objectTreeView.name = item.basename;
                objectTreeView.dateDepot = item.created;
                objectTreeView.repondant = item.author.first_name + ' ' + item.author.last_name;
                objectTreeView._id = 'file';
                objectTreeView.id = questionnaireId + '-' + themeId + '-' + questionId + '-' + item.id;
                objectTreeView.url = item.url;
            } else if (themeId != null && questionId == null) { // Question
                objectTreeView.name = item.title || item.description;
                objectTreeView._children = [];
                objectTreeView._id = 'question';
                objectTreeView.id = questionnaireId + '-' + themeId + '-' + item.id;
            } else if (questionnaireId !== null && themeId === null) { // Theme
                objectTreeView.name = item.title || item.description;
                objectTreeView._children = [];
                objectTreeView._id = 'theme';
                objectTreeView.id = questionnaireId + '-' + item.id;
            } else { // Questionnaire
                objectTreeView.name = item.title || item.description;
                objectTreeView._children = [];
                objectTreeView._id = 'questionnaire';
                objectTreeView.id = item.id;
            }

            return objectTreeView;
        },

        questionnaireDetailUrl(questionnaireId) {
            return backendUrls['questionnaire-detail'](questionnaireId)
        },

        showModal(qId) {
          this.questionnaireId = qId
          $(this.$refs.modal.$el).modal('show')
        },

        cloneQuestionnaire() {
          let self = this;
          const getCreateMethod = () => axios.post.bind(this, backendUrls.questionnaire())
          const getUpdateMethod = (qId) => axios.put.bind(this, backendUrls.questionnaire(qId))

          console.log(this.checkedCtrls);
          console.log(this.checkedCtrls.length);
          if (this.checkedCtrls.length) {
            const curQ = this.control.questionnaires.find(q => q.id === this.questionnaireId)
            const destCtrls = this.controls.filter(ctrl => this.checkedCtrls.includes(ctrl.id))
            console.log(destCtrls);

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

        exportControl(itemId, type) {
          this.checkedElements = [];
          this.checkedElements.push(itemId);

          const formatFilename = (rf) => {
            const questionnaireNb = String(rf.questionnaireNb).padStart(2, '0')
            const themeId = String(rf.themeId + 1).padStart(2, '0')
            const questionId = String(rf.questionId + 1).padStart(2, '0')
            const filename = `Q${questionnaireNb}-T${themeId}-${questionId}-${rf.basename}`
            return { questionnaireNb, themeId, filename }
          }

          let questionnaireId = '';
          let themeId = '';
          let questionId = '';
          let fileId = '';
          let responseFiles = '';

          if (type === 'questionnaire') {
            questionnaireId = itemId.toString().split('-')[0];
            responseFiles = this.accessibleQuestionnaires
            .filter(aq => this.checkedElements.includes(aq.id))
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
          } else if (type === 'theme') {
            questionnaireId = itemId.toString().split('-')[0];
            themeId = itemId.toString().split('-')[1];
            responseFiles = this.accessibleQuestionnaires
            .filter(aq => aq.id.toString() === questionnaireId)
            .flatMap(fq => {
              if (fq.themes) {
                return fq.themes
                  .filter(t => t.id.toString() === themeId)
                  .flatMap(t => {
                  if (t.questions) {
                    return t.questions.flatMap(q => {
                      return q.response_files.flatMap(rf => {
                        if (rf) {
                          return {
                            questionnaireNb: fq.numbering,
                            themeId: t.order,
                            questionId: q.order,
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
          } else if (type === 'question') {
            questionnaireId = itemId.toString().split('-')[0];
            themeId = itemId.toString().split('-')[1];
            questionId = itemId.toString().split('-')[2];
            responseFiles = this.accessibleQuestionnaires
            .filter(aq => aq.id.toString() === questionnaireId)
            .flatMap(fq => {
              if (fq.themes) {
                return fq.themes
                  .filter(t => t.id.toString() === themeId)
                  .flatMap(t => {
                  if (t.questions) {
                    return t.questions
                      .filter(q => q.id.toString() === questionId)
                      .flatMap(q => {
                      return q.response_files.flatMap(rf => {
                        if (rf) {
                          return {
                            questionnaireNb: fq.numbering,
                            themeId: t.order,
                            questionId: q.order,
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
          } else {
            questionnaireId = itemId.split('-')[0];
            themeId = itemId.split('-')[1];
            questionId = itemId.split('-')[2];
            fileId = itemId.split('-')[3];
            questionnaireId = itemId.split('-')[0];
            themeId = itemId.split('-')[1];
            questionId = itemId.split('-')[2];
            responseFiles = this.accessibleQuestionnaires
            .filter(aq => aq.id.toString() === questionnaireId)
            .flatMap(fq => {
              if (fq.themes) {
                return fq.themes
                  .filter(t => t.id.toString() === themeId)
                  .flatMap(t => {
                  if (t.questions) {
                    return t.questions
                      .filter(q => q.id.toString() === questionId)
                      .flatMap(q => {
                      return q.response_files
                        .filter(rf => rf.id.toString() === fileId)
                        .flatMap(rf => {
                        if (rf) {
                          return {
                            questionnaireNb: fq.numbering,
                            themeId: t.order,
                            questionId: q.order,
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
          }

          const zipFilename = this.control.reference_code + '.zip'
          const zip = new JSZip()
          let cnt = 0

          responseFiles
                    .filter(respFile => respFile.is_deleted === false)
                    .map(rf => {
            const url = window.location.origin + rf.url

            JSZipUtils.getBinaryContent(url, (err, data) => {
              if (err) throw err

              const formatted = formatFilename(rf)

              zip.folder(`Q${formatted.questionnaireNb}`)
                .folder(`T${formatted.themeId}`)
                .file(formatted.filename, data, { binary: true })

              cnt++
              if (cnt === responseFiles.length) {
                zip.generateAsync({ type: 'blob' }).then((content) => {
                  saveAs(content, zipFilename)
                })
              }
            })
          })
        },
    },

    mounted() {
      this.getUsers();
    },
});
</script>

<style>
    .leftAlign {
        text-align: left;
    }
</style>