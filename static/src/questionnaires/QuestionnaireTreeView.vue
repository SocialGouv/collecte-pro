<template>
    <div id="app">
        <vue-ads-table
            :columns="columns"
            :rows="accessibleQuestionnaires"
        >
            <!-- Will be applied on the name column for the rows with an _id of tiger -->
            <template slot="name" slot-scope="props">{{ props.row.name }}</template>
            <template slot="name_file" slot-scope="props"><a href="">{{ props.row.name }}</a></template>
            <template slot="dateDepot" slot-scope="props">{{ props.row.dateDepot }}</template>
            <template slot="repondant" slot-scope="props">{{ props.row.repondant }}</template>
            <template slot="action_questionnaire" slot-scope="props">
                <div class="btn-group">
                    <a
                      href=""
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
                      >
                        <i class="fe fe-copy"></i>
                        Dupliquer
                      </button>
                    </div>
                </div>
            </template>
            <template slot="action_file" slot-scope="props">
                <button
                    class="btn btn-secondary"
                    type="button"
                >
                    <i class="fas fa-file-export"></i>
                    Télécharger
                </button>
            </template>
            <template slot="no-rows">Pas de résultats</template>
            <template slot="toggle-children-icon" slot-scope="props"></template>
        </vue-ads-table>
    </div>
</template>

<script>
import '../../../node_modules/@fortawesome/fontawesome-free/css/all.min.css';
import '../../../node_modules/vue-ads-table-tree/dist/vue-ads-table-tree.css';
import Vue from 'vue';
import { VueAdsTable } from 'vue-ads-table-tree';

export default Vue.extend({
    props: {
        control: {type: Object, default: () => ({})}
    },
    components: {
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
        };
    },

    computed: {
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
                _id: ''
            };

            if (hasFiles) {
                objectTreeView.name = item.basename;
                objectTreeView.dateDepot = item.created;
                objectTreeView.repondant = item.author.first_name + ' ' + item.author.last_name;
                objectTreeView._id = 'file';
            } else if (isQuestionnaire) {
                objectTreeView.name = item.title || item.description;
                objectTreeView._children = [];
                objectTreeView._id = 'questionnaire';
            } else {
                objectTreeView.name = item.title || item.description;
                objectTreeView._children = [];
            }

            return objectTreeView;
        }
    },
});
</script>

<style>
    .leftAlign {
        text-align: left;
    }
</style>