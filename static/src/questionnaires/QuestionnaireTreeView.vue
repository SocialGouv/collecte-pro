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

<script lang="ts">
import { defineComponent, ref, computed, onMounted } from 'vue'
import { useStore } from 'vuex'
import axios from 'axios'
import JSZip from 'jszip'
import JSZipUtils from 'jszip-utils'
import { saveAs } from 'file-saver'

import backendUrls from '../utils/backend'
import InfoBar from '../utils/InfoBar.vue'
import fr from '../utils/vuejs-datepicker-locale-fr'

export default defineComponent({
  name: 'QuestionnaireFiles',
  props: {
    control: { type: Object, default: () => ({}) }
  },
  components: {
    InfoBar
  },
  setup(props) {
    const store = useStore()
    
    // ----------------------
    // Réactivité
    // ----------------------
    const columns = ref([
      { property: 'name', title: 'Document' },
      { property: 'dateDepot', title: 'Date de dépôt', filterable: true },
      { property: 'repondant', title: 'Répondant', filterable: true },
    ])
    
    const classes = ref({
      selected: { selected_row: true },
      group: { 'vue-ads-font-bold': true, 'vue-ads-border-b': true, 'vue-ads-italic': true },
      'all/': { 'vue-ads-border-b': true, 'vue-ads-border-l': true, 'vue-ads-text-left': true },
      'even/': { 'vue-ads-bg-white': true, 'selectable_row': true },
      'odd/': { 'vue-ads-bg-gray-100': true, 'selectable_row': true },
      '0/': { 'vue-ads-border-t': true },
      '/0_': { 'vue-ads-border-r': true, 'vue-ads-text-sm': true, 'vue-ads-py-2': true, 'vue-ads-px-4': true },
    })
    
    const filter = ref('')
    const date_filter_start = ref<Date | ''>('')
    const date_filter_end = ref<Date | ''>('')
    const selected = ref<any[]>([])
    const repondantsListe = ref<any[]>([])
    const treeViewElements = ref<any[]>([])
    
    const frLocale = fr
    
    // ----------------------
    // Computed
    // ----------------------
    const accessibleControls = computed(() => store.state.controls)
    const accessibleQuestionnaires = computed(() =>
      props.control.questionnaires.filter((q: any) => !q.is_draft)
    )
    
    // ----------------------
    // Méthodes
    // ----------------------
    const getUsers = async () => {
      try {
        const resp = await axios.get(backendUrls.getDepositorsInControl(props.control.id))
        repondantsListe.value = resp.data
      } catch (err) {
        console.error('Erreur lors de la récupération des répondants :', err)
      }
    }
    
    const refreshFiles = () => {
      const controlQuestionnaires = props.control.questionnaires.filter((q: any) => !q.is_draft)
      treeViewElements.value = getTreeViewElements(controlQuestionnaires)
      // Eventuelles manipulations DOM pour accessibilité
      setTimeout(() => {
        // Titles et tabindex sur les lignes
      }, 200)
    }
    
    const filterByDate = (responseFile: any) => {
      if (!responseFile.created) return false
      const creation_date = new Date(responseFile.created)
      if (!date_filter_start.value && !date_filter_end.value) return true
      if (date_filter_start.value && date_filter_end.value) {
        return date_filter_start.value <= creation_date && creation_date <= date_filter_end.value
      } else if (date_filter_start.value) {
        return date_filter_start.value <= creation_date
      } else if (date_filter_end.value) {
        return creation_date <= date_filter_end.value
      }
      return true
    }
    
    const pickFiles = (selected_id = '') => {
      const filterVal = filter.value
      return treeViewElements.value.flatMap((questionnaire: any) => {
        if (!questionnaire._children) return []
        return questionnaire._children.flatMap((theme: any) => {
          if (!theme._children) return []
          return theme._children.flatMap((question: any) => {
            if (!question._children) return []
            return question._children
              .filter((file: any) => !filterVal || file.repondant === filterVal)
              .filter((file: any) => file.id.startsWith(selected_id))
          })
        })
      })
    }
    
    const zipFiles = (files: any[]) => {
      const zip = new JSZip()
      let cnt = 0
      const zipFilename = props.control.reference_code + '.zip'
      
      files.forEach((file) => {
        const url = window.location.origin + file.url
        JSZipUtils.getBinaryContent(url, (err: any, data: any) => {
          if (err) throw err
          zip.file(file.basename, data, { binary: true })
          cnt++
          if (cnt === files.length) {
            zip.generateAsync({ type: 'blob' }).then((content) => saveAs(content, zipFilename))
          }
        })
      })
    }
    
    const exportSelected = () => zipFiles(pickFiles())
    const exportAll = () => zipFiles(pickFiles())
    
    // ----------------------
    // Lifecycle
    // ----------------------
    onMounted(() => {
      getUsers()
      refreshFiles()
    })
    
    // ----------------------
    // Retour des refs et méthodes
    // ----------------------
    return {
      columns,
      classes,
      filter,
      date_filter_start,
      date_filter_end,
      selected,
      repondantsListe,
      treeViewElements,
      frLocale,
      accessibleControls,
      accessibleQuestionnaires,
      getUsers,
      refreshFiles,
      filterByDate,
      pickFiles,
      zipFiles,
      exportSelected,
      exportAll,
    }
  }
})
</script>
