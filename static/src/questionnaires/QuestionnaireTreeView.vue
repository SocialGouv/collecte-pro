<template>
    <div id="app" class="card">
        <div class="p-4 font-italic text-muted">
            Pour sélectionner les éléments à exporter, cliquer sur les lignes concernées à l’aide de la touche MAJ ou Ctrl enfoncée.
        </div>
        <div class="card">
          <span class="form-inline">
            <span class="form-group col-sm-4">
              <span class="form-label mr-2">Filtrer par répondant</span>
              <select v-model="filter" class="form-control">
                <option></option>
                <option v-for="option in repondantsListe" :key="option">
                  {{ option.first_name + ' ' + option.last_name }}
                </option>
              </select>
            </span>
            <span class="form-group col-sm-5">
              <label class="form-label mr-2" id="filtre_start_date" for="filtre_startdate">
                Filtrer par date de dépôt de
              </label>
              <datepicker id="filtre_startdate"
                class="form-control date-input"
                aria-labelledby="filtre_start_date"
                v-model="date_filter_start"
                :language="fr"
                :typeable="true"
                :placeholder="placeholder"
                :format="format"
                :monday-first="true">
              </datepicker>
              <label class="form-label ml-2 mr-2" id="filtre_end_date" for="filtre_enddate">à</label>
              <datepicker id="filtre_enddate"
                class="form-control date-input"
                aria-labelledby="filtre_end_date"
                v-model="date_filter_end"
                :language="fr"
                :typeable="true"
                :placeholder="placeholder"
                :format="format"
                :monday-first="true">
              </datepicker>
            </span>
            <span class="form-group col-sm-3" v-if="filter!=='' || !(!this.date_filter_start && !this.date_filter_end)">
              <button @click="exportFiltered" type="button" class="btn btn-secondary" :disabled="this.repondantsListe.length==0">
                <span class="fa-file-export fas mr-2" aria-hidden="true"></span>
                Exporter les documents filtrés
              </button>
            </span>
            <span class="form-group col-sm-3" v-else-if="this.selected.length">
              <button @click="exportSelected" type="button" class="btn btn-secondary" :disabled="this.repondantsListe.length==0">
                <span class="fa-file-export fas mr-2" aria-hidden="true"></span>
                Exporter les documents sélectionnés
              </button>
            </span>
            <span class="form-group col-sm-3" v-else>
              <button @click="exportAll" type="button" class="btn btn-secondary" :disabled="this.repondantsListe.length==0">
                <span class="fa-file-export fas mr-2" aria-hidden="true"></span>
                Exporter tous les documents
              </button>
            </span>
          </span>
        </div>
        <div class="card">
        <vue-ads-table
            :columns="columns"
            :classes="classes"
            :rows="treeViewElements"
            :selectable=true
            :filter="filter"
            @selection-change="selectionChange"
        >
            <template v-slot:item.data-table-select="{ item, isSelected }">
                <v-checkbox
                    :value="isSelected"
                     hide-details
                     class="mt-0"
                     @change="onItemSelect({ item, value: !isSelected })"
                 >
                </v-checkbox>
            </template>
            <template slot="name" slot-scope="props">{{ props.row.name }}</template>
            <template slot="name_file" slot-scope="props">
              <a :href="props.row.url" target="_blank"
                rel="noopener noreferrer"
                class="btn tag tag-azure pull-left btn-file"
                :title="props.row.name">
                {{ props.row.short_name }}
                <span class="tag-addon pb-1">
                  <span class="fe fe-file" aria-hidden="true"></span>
                </span>
              </a>
            </template>
            <template slot="name_fileAnnexe" slot-scope="props">
              <a :href="props.row.url" target="_blank"
                rel="noopener noreferrer"
                class="btn tag tag-orange pull-left btn-file"
                :title="props.row.name">
                {{ props.row.short_name }}
                <span class="tag-addon pb-1">
                  <span class="fe fe-paperclip" aria-hidden="true"></span>
                </span>
              </a>
            </template>
            <template slot="name_filePieceJointe" slot-scope="props">
              <a :href="props.row.url" target="_blank"
                rel="noopener noreferrer"
                class="btn tag tag-orange pull-left btn-file"
                :title="props.row.name">
                {{ props.row.short_name }}
                <span class="tag-addon pb-1">
                  <span class="fe fe-paperclip" aria-hidden="true"></span>
                </span>
              </a>
            </template>
            <template slot="name_filePieceJointe" slot-scope="props">
              <a :href="props.row.url" target="_blank"
                rel="noopener noreferrer"
                class="btn tag tag-orange pull-left btn-file"
                :title="props.row.name">
                {{ props.row.short_name }}
                <span class="tag-addon pb-1">
                  <span class="fe fe-paperclip" aria-hidden="true"></span>
                </span>
              </a>
            </template>
            <template slot="name_fileCorbeille" slot-scope="props">
              <a :href="props.row.url" target="_blank"
                rel="noopener noreferrer"
                class="btn tag tag-azure pull-left btn-file"
                :title="props.row.name">
                {{ props.row.short_name }}
                <span class="tag-addon pb-1">
                  <span class="fe fe-trash-2" aria-hidden="true"></span>
                </span>
              </a>
            </template>
            <template slot="dateDepot" slot-scope="props">{{ props.row.dateDepot }}</template>
            <template slot="repondant" slot-scope="props">{{ props.row.repondant }}</template>
            <template slot="no-rows">Pas de résultat</template>
            <template slot="toggle-children-icon" slot-scope="props">
              <span class="fe fe-folder-minus" v-if="props.expanded" aria-hidden="true"></span>
              <span class="fe fe-folder-plus" v-else aria-hidden="true"></span>
              &nbsp;
            </template>
        </vue-ads-table>
        </div>
    </div>
</template>

<script>
import '../../css/questionnaires.css'
import axios from 'axios';
import backendUrls from '../utils/backend';

import '../../../node_modules/@fortawesome/fontawesome-free/css/all.min.css';
import '../../../node_modules/vue-ads-table-tree/dist/vue-ads-table-tree.css';

import InfoBar from '../utils/InfoBar'

import Vue from 'vue';
import { mapState } from 'vuex'
import { VueAdsTable } from 'vue-ads-table-tree';

import JSZip from 'jszip'
import JSZipUtils from 'jszip-utils'
import { saveAs } from 'file-saver'

import Datepicker from 'vuejs-datepicker';
import fr from '../utils/vuejs-datepicker-locale-fr';

export default Vue.extend({
    props: {
        control: {type: Object, default: () => ({})}
    },
    components: {
        InfoBar,
        VueAdsTable,
        Datepicker,
    },

    data () {
        let columns = [
            {
                property: 'name',
                title: 'Document',
            },
            {
                property: 'dateDepot',
                title: 'Date de dépôt',
                filterable: true,
            },
            {
                property: 'repondant',
                title: 'Répondant',
                filterable: true,
            },
        ];

        let classes = {
            selected: {
              'selected_row': true,
            },
            group: {
              'vue-ads-font-bold': true,
              'vue-ads-border-b': true,
              'vue-ads-italic': true,
            },
            'all/': {
              'vue-ads-border-b': true,
              'vue-ads-border-l': true,
              'vue-ads-text-left': true,
            },
            'even/': {
              'vue-ads-bg-white': true,
              'selectable_row': true,
            },
            'odd/': {
              'vue-ads-bg-gray-100': true,
              'selectable_row': true,
            },
            '0/': {
              'vue-ads-border-t': true,
            },
            '/0_': {
              'vue-ads-border-r': true,
              'vue-ads-text-sm': true,
              'vue-ads-py-2': true,
              'vue-ads-px-4': true,
            },
        };

        return {
            columns,
            classes,
            filter: '',
            date_filter_start: '',
            date_filter_end: '',
            fr: fr, // locale for datepicker
            format: "yyyy-MM-dd", // format for datepicker
            placeholder: "yyyy-mm-dd", // Placeholder for datepicker
            selected: [],
            checkedCtrls: [],
            checkedElements: [],
            repondantsListe: [],
            treeViewElements: []
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
    },

    watch: {
        'filter': function(val, oldVal) {
            this.selected = [];
            this.refreshFiles();
        },
        'date_filter_start': function(val, oldVal) {
          if (this.date_filter_start) {
            this.date_filter_start.setHours(0,0,0,0);
            this.selected = [];
            this.refreshFiles();
          }else{
            this.selected = [];
            this.refreshFiles();
          }
        },
        'date_filter_end': function(val, oldVal) {
          if (this.date_filter_end) {
            this.date_filter_end.setHours(0,0,0,0);
            this.selected = [];
            this.refreshFiles();
          }else{
            this.selected = [];
            this.refreshFiles();
          }
        }
    },
    methods: {
        selectionChange(rows) {
          this.selected = rows;
        },
        exportFiltered(event) {
          if (this.selected.length > 0) {
            this.exportSelected();
          } else {
            this.exportAll();
          }
        },
        exportSelected(event) {
          function onlyUnique(value, index, self) {
            for (let i=0;i<self.length;i++) {
              if (self[i].id == value.id) {
                return i === index;
              }
            }
          }
          let files = [];
          for (let i=0; i< this.selected.length; i++) {
            files.push.apply(files, this.pickFiles(this.selected[i].id))
          }
          this.zipFiles(files.filter(onlyUnique));
        },
        exportAll(event) {
          this.zipFiles(this.pickFiles());
        },
        pickFiles(selected_id='') {
          let filter = '' + this.filter;
          let files = this.treeViewElements.flatMap(questionnaire => {
            if (questionnaire._children) {
              return questionnaire._children.flatMap(theme => {
                if (theme._id == 'theme' && theme._children) {
                  return theme._children.flatMap(question => {
                    if (question._children) {
                      return question._children.flatMap(file => {
                        if (file) {
                          if (!filter || file.repondant == filter) {
                            return {
                              questionnaireNb: questionnaire.order,
                              themeId: theme.order,
                              questionId: question.order,
                              category: 'response_file',
                              id: file.id,
                              basename: file.name,
                              url: file.url,
                              is_deleted: file.is_deleted,
                            }
                          }
                        }
                      })
                    }
                  })
                } else if (theme._id == 'corbeille' && theme._children) {
                  return theme._children.flatMap(file => {
                    if (file) {
                      if (!filter || file.repondant == filter) {
                        return {
                          questionnaireNb: questionnaire.order,
                          themeId: 0,
                          questionId: 0,
                          category: 'response_file',
                          id: file.id,
                          basename: file.name,
                          url: file.url,
                          is_deleted: file.is_deleted,
                        }
                      }
                    }
                  })
                } else if (theme._id == 'annexes' && theme._children) {
                  return theme._children.flatMap(file => {
                    if (file) {
                      if (!filter) {
                        return {
                          questionnaireNb: questionnaire.order,
                          themeId: 0,
                          questionId: 0,
                          category: 'question_file',
                          id: file.id,
                          basename: file.name,
                          url: file.url,
                          is_deleted: file.is_deleted,
                        }
                      }
                    }
                  })
                }
              })
            }
          });
          return files.filter(
            file => typeof(file)!=="undefined"
          ).filter(
            file => file.id.startsWith(selected_id)
          );
        },
        zipFiles(files) {
          this.$parent.$parent.$children[0].loaderActive = true;
          const formatFilename = (file) => {
            const questionnaireNb = String(file.questionnaireNb).padStart(2, '0');
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
          const zipFilename = this.control.reference_code + '.zip'
          const zip = new JSZip()
          let cnt = 0

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
                  this.$parent.$parent.$children[0].loaderActive = false;
                  saveAs(content, zipFilename)
                })
              }
            })
          })
        },
        refreshFiles() {
          const controlQuestionnaires = this.control.questionnaires.filter(q => !q.is_draft);
          this.treeViewElements = this.getTreeViewElements(controlQuestionnaires);
          $("table tbody tr").attr("tabindex", 0);
          $("table tbody tr").off("keyup");
          $("table tbody tr").keyup(function(event){
            if (event.which != 13) {
              return;
            }
            event.target.click();
          });
          window.setTimeout(() => {
            $("table tbody tr td span:contains('Questionnaire ')").parent().parent().attr("title", "Sélectionner tous les documents du questionnaire");
            $("table tbody tr td span:contains('Thème ')").parent().parent().attr("title", "Sélectionner tous les documents du thème");
            $("table tbody tr td span:contains('Question ')").parent().parent().attr("title", "Sélectionner tous les documents de la question");
          }, 200);
        },
        filterByDate(responseFile) {
          let creation_date = new Date(responseFile.created);
          if (!this.date_filter_start && !this.date_filter_end) {
            return true;
          }
          if (!responseFile.created) {
            return false;
          }
          try {
            if (this.date_filter_start && this.date_filter_end) {
              if (this.date_filter_start <= creation_date && creation_date <= this.date_filter_end) {
                return true;
              }
              return false;
            } else if (this.date_filter_start) {
              if (this.date_filter_start <= creation_date) {
                return true;
              }
              return false;
            } else if (this.date_filter_end) {
                if (creation_date <= this.date_filter_end) {
                  return true;
                }
                return false;
            }
          } catch(error) {
            return true;
          }
          return true;
        },
        getUsers() {
          axios.get(backendUrls.getDepositorsInControl(this.control.id))
            .then((response) => {
              this.repondantsListe = response.data;
            })
        },
        /**
         * get formatted item for treeview plugin
         */
        getTreeViewLevel(item, questionnaireId = null, themeId = null,
          questionId = null, isAnnexe = false, isCorbeille = false,
          isFichierAnnexe = false, isFichierCorbeille = false, isPieceJointe = false, isFichierPieceJointe = false) {
            const maxLength = 100;
            const objectTreeView = {
                name: '',
                short_name: '',
                dateDepot: '',
                repondant: '',
                _showChildren: true,
                _children: [],
                _id: '',
                id: '',
                url: '',
                order: 0,
                is_deleted: ''
            };

            if (isAnnexe) { // Annexes
                objectTreeView.name = 'Annexes';
                objectTreeView._children = [];
                objectTreeView._id = 'annexes';
                objectTreeView.id = questionnaireId + '-' + 'annexes';
            } else if (isPieceJointe) { // Questionnaire pièces jointes
                objectTreeView.name = 'Pièces jointes';
                objectTreeView._children = [];
                objectTreeView._id = 'piecesjointes';
                objectTreeView.id = questionnaireId + '-' + 'piecesjointes';
            } else if (isCorbeille) { // Corbeille
                objectTreeView.name = 'Corbeille';
                objectTreeView._children = [];
                objectTreeView._id = 'corbeille';
                objectTreeView.id = questionnaireId + '-' + 'corbeille';
            } else if (isFichierAnnexe) { // Fichier annexe
                objectTreeView.name = item.basename;
                objectTreeView.short_name = (item.basename.length > maxLength) ? item.basename.slice(0, maxLength) + '...' : item.basename;
                objectTreeView.url = item.url;
                objectTreeView._showChildren = false;
                objectTreeView._id = 'fileAnnexe';
                objectTreeView.id = questionnaireId + '-' + 'annexes' + '-' + item.id;
            } else if (isFichierPieceJointe) { // Fichier pièce jointe
                objectTreeView.name = item.basename;
                objectTreeView.short_name = (item.basename.length > maxLength) ? item.basename.slice(0, maxLength) + '...' : item.basename;
                objectTreeView.url = item.url;
                objectTreeView._showChildren = false;
                objectTreeView._id = 'filePieceJointe';
                objectTreeView.id = questionnaireId + '-' + 'piecesjointes' + '-' + item.id;
            } else if (isFichierCorbeille) { // Fichier corbeille
                objectTreeView.name = item.basename;
                objectTreeView.short_name = (item.basename.length > maxLength) ? item.basename.slice(0, maxLength) + '...' : item.basename;
                objectTreeView.dateDepot = this.formatDate(new Date(item.created));
                objectTreeView.repondant = item.author.first_name + ' ' + item.author.last_name;
                objectTreeView.url = item.url;
                objectTreeView._showChildren = false;
                objectTreeView._id = 'fileCorbeille';
                objectTreeView.id = questionnaireId + '-' + 'corbeille' + '-' + item.id;
                objectTreeView.is_deleted = item.is_deleted;
            } else if (questionId != null) { // Response_file
                objectTreeView.name = item.basename;
                objectTreeView.short_name = (item.basename.length > maxLength) ? item.basename.slice(0, maxLength) + '...' : item.basename;
                objectTreeView.dateDepot = this.formatDate(new Date(item.created));
                objectTreeView.repondant = item.author.first_name + ' ' + item.author.last_name;
                objectTreeView._id = 'file';
                objectTreeView.id = questionnaireId + '-' + themeId + '-' + questionId + '-' + item.id;
                objectTreeView.url = item.url;
                objectTreeView.is_deleted = item.is_deleted;
            } else if (themeId != null && questionId == null) { // Question
                objectTreeView.name = 'Question ' + (item.order+1) + ' - ' + (item.title || item.description);
                objectTreeView._children = [];
                objectTreeView._id = 'question';
                objectTreeView.id = questionnaireId + '-' + themeId + '-' + item.id;
                objectTreeView.order = item.order;
            } else if (questionnaireId !== null && themeId === null) { // Theme
                objectTreeView.name = 'Thème ' + (item.order+1) + ' - ' + (item.title || item.description);
                objectTreeView._children = [];
                objectTreeView._id = 'theme';
                objectTreeView.id = questionnaireId + '-' + item.id;
                objectTreeView.order = item.order;
            } else { // Questionnaire
                objectTreeView.name = 'Questionnaire ' + item.numbering + ' - ' + (item.title || item.description);
                objectTreeView._children = [];
                objectTreeView._id = 'questionnaire';
                objectTreeView.id = item.id;
                objectTreeView.order = item.numbering;
            }

            return objectTreeView;
        },

        questionnaireDetailUrl(questionnaireId) {
            return backendUrls['questionnaire-detail'](questionnaireId)
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
        getTreeViewElements(accessibleQuestionnaires) {
            return accessibleQuestionnaires.map(element => {
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
                                                                    .filter(this.filterByDate)
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

                const objAnnexes = this.getTreeViewLevel(null, element.id, null, null, true);
                const objCorbeille = this.getTreeViewLevel(null, element.id, null, null, false, true);
                const objPiecesJointes = this.getTreeViewLevel(null, element.id, null, null, false, false, false, false, true);

                objPiecesJointes._children = accessibleQuestionnaires
                  .filter(aq => aq.id === element.id)
                  .flatMap(fq => {
                    return fq.questionnaire_files
                    .filter(this.filterByDate)
                    .flatMap(qf => {
                        if (qf) {
                          return this.getTreeViewLevel(qf, element.id, null, null, false, false, false, false, false, true);
                        }
                    })
                  })

                objAnnexes._children = accessibleQuestionnaires
                  .filter(aq => aq.id === element.id)
                  .flatMap(fq => {
                    if (fq.themes) {
                      return fq.themes.flatMap(t => {
                        if (t.questions) {
                          return t.questions.flatMap(q => {
                            return q.question_files
                              .filter(this.filterByDate)
                              .flatMap(qf => {
                                if (qf) {
                                  return this.getTreeViewLevel(qf, element.id, null, null, false, false, true);
                                }
                            })
                          })
                        }
                      })
                    }
                  })

                objCorbeille._children = accessibleQuestionnaires
                  .filter(aq => aq.id === element.id)
                  .flatMap(fq => {
                    if (fq.themes) {
                      return fq.themes.flatMap(t => {
                        if (t.questions) {
                          return t.questions.flatMap(q => {
                            return q.response_files
                              .filter(rf => rf.is_deleted === true)
                              .filter(this.filterByDate)
                              .flatMap(rf => {
                              if (rf) {
                                return this.getTreeViewLevel(rf, element.id, null, null, false, false, false, true);
                              }
                            })
                          })
                        }
                      })
                    }
                  })

                if (!objCorbeille._children.length) {
                  objCorbeille._showChildren = false;
                } else {
                  objQuestionnaire._children.unshift(objCorbeille);
                }

                if (!objAnnexes._children.length) {
                  objAnnexes._showChildren = false;
                } else {
                  objQuestionnaire._children.unshift(objAnnexes);
                }

                if (!objPiecesJointes._children.length) {
                  objPiecesJointes._showChildren = false;
                } else {
                  objQuestionnaire._children.unshift(objPiecesJointes);
                }

                return objQuestionnaire;
            });
        },
        formatDate(dateDepot) {
            let finalDate = "";
            if (dateDepot.getDate() < 10) {
                finalDate += "0" + dateDepot.getDate() + "/";
            } else {
                finalDate += dateDepot.getDate() + "/";
            }
            if (dateDepot.getMonth() < 9) {
                finalDate += "0" + (dateDepot.getMonth()+1) + "/";
            } else {
                finalDate += (dateDepot.getMonth()+1) + "/";
            }
            finalDate += (1900+dateDepot.getYear()) + " ";
            if (dateDepot.getHours() < 10) {
                finalDate += "0" + dateDepot.getHours() + ":";
            } else {
                finalDate += dateDepot.getHours() + ":";
            }
            if (dateDepot.getMinutes() < 10) {
                finalDate += "0" + dateDepot.getMinutes();
            } else {
                finalDate += "" + dateDepot.getMinutes();
            }

            return finalDate;
        }
    },

    mounted() {
      this.getUsers();
      this.refreshFiles();
    },
});
</script>
