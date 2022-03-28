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
        <vue-ads-table
            :columns="columns"
            :rows="accessibleQuestionnaires"
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
                    </div>
                </div>
            </template>
            <template slot="action_file" slot-scope="props">
                <a
                    :href="props.row.url"
                    class="btn btn-secondary"
                >
                    <i class="fas fa-file-export"></i>
                    Télécharger
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
import Vuex, { mapState } from 'vuex'
import { VueAdsTable } from 'vue-ads-table-tree';

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
            },
            {
                property: 'repondant',
                title: 'Répondant',
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
            start: 0,
            end: 2,
            checkedCtrls: [],
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
            const qstnr = this.control.questionnaires.filter((questionnaire) => !questionnaire.is_draft);

            return qstnr.map(element => {
                const objQuestionnaire = this.getTreeViewLevel(element, false, true);

                if (
                    Object.prototype.hasOwnProperty.call(element, 'themes') &&
                    element.themes.length
                ) {
                    objQuestionnaire._children = element.themes.map(theme => {
                        const objTheme = this.getTreeViewLevel(theme);

                        if (
                            Object.prototype.hasOwnProperty.call(theme, 'questions') &&
                            theme.questions.length
                        ) {
                            objTheme._children = theme.questions.map(question => {
                                const objQuestion = this.getTreeViewLevel(question);

                                if (
                                    Object.prototype.hasOwnProperty.call(question, 'response_files') &&
                                    question.response_files.length
                                ) {
                                    objQuestion._children = question.response_files.map(responseFile => this.getTreeViewLevel(responseFile, true));

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

                return objQuestionnaire;
            });
        },
    },
    methods: {
        /**
         * get formatted item for treeview plugin
         */
        getTreeViewLevel(item, hasFiles = false, isQuestionnaire = false) {
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

            if (hasFiles) {
                objectTreeView.name = item.basename;
                objectTreeView.dateDepot = item.created;
                objectTreeView.repondant = item.author.first_name + ' ' + item.author.last_name;
                objectTreeView._id = 'file';
                objectTreeView.url = item.url;
            } else if (isQuestionnaire) {
                objectTreeView.name = item.title || item.description;
                objectTreeView._children = [];
                objectTreeView._id = 'questionnaire';
                objectTreeView.id = item.id;
            } else {
                objectTreeView.name = item.title || item.description;
                objectTreeView._children = [];
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
    },
});
</script>

<style>
    .leftAlign {
        text-align: left;
    }
</style>