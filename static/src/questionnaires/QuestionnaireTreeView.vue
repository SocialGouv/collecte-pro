<template>
  <div id="app" class="card">
    <div class="p-4 font-italic text-muted">
      Pour sélectionner les éléments à exporter, cliquer sur les lignes concernées à l'aide de la touche MAJ ou Ctrl enfoncée.
    </div>
    <div class="card">
      <span class="form-inline">
        <span class="form-group col-sm-4">
          <span class="form-label mr-2">Filtrer par répondant</span>
          <select v-model="filter" class="form-control">
            <option></option>
            <option v-for="option in repondantsListe" :key="optionKey(option)" :value="option.first_name + ' ' + option.last_name">
              {{ option.first_name + ' ' + option.last_name }}
            </option>
          </select>
        </span>
        <span class="form-group col-sm-5">
          <label class="form-label mr-2" id="filtre_start_date" for="filtre_startdate">Filtrer par date de dépôt de</label>
          <Datepicker id="filtre_startdate" class="form-control date-input" aria-labelledby="filtre_start_date" v-model="date_filter_start" :locale="frLocale" :typeable="true" :placeholder="placeholder" :format="format" :monday-first="true" />
          <label class="form-label ml-2 mr-2" id="filtre_end_date" for="filtre_enddate">à</label>
          <Datepicker id="filtre_enddate" class="form-control date-input" aria-labelledby="filtre_end_date" v-model="date_filter_end" :locale="frLocale" :typeable="true" :placeholder="placeholder" :format="format" :monday-first="true" />
        </span>
        <span class="form-group col-sm-3" v-if="filter!=='' || !(!date_filter_start && !date_filter_end)">
          <button @click="exportFiltered" type="button" class="btn btn-secondary" :disabled="repondantsListe.length==0">
            <span class="fa-file-export fas mr-2" aria-hidden="true"></span>
            Exporter les documents filtrés
          </button>
        </span>
        <span class="form-group col-sm-3" v-else-if="selected.length">
          <button @click="exportSelected" type="button" class="btn btn-secondary" :disabled="repondantsListe.length==0">
            <span class="fa-file-export fas mr-2" aria-hidden="true"></span>
            Exporter les documents sélectionnés
          </button>
        </span>
        <span class="form-group col-sm-3" v-else>
          <button @click="exportAll" type="button" class="btn btn-secondary" :disabled="repondantsListe.length==0">
            <span class="fa-file-export fas mr-2" aria-hidden="true"></span>
            Exporter tous les documents
          </button>
        </span>
      </span>
    </div>

    <div class="card">
      <table class="tree-table">
        <thead>
          <tr>
            <th class="col-expand"></th>
            <th class="col-checkbox"></th>
            <th class="col-document">Document</th>
            <th class="col-date">Date de dépôt</th>
            <th class="col-repondant">Répondant</th>
          </tr>
        </thead>
        <tbody>
          <TreeNode 
            v-for="row in treeViewElements" 
            :key="row.id" 
            :node="row"
            :selected="selected"
            @toggle="toggleNode"
            @select="selectNode"
          />
          <tr v-if="treeViewElements.length === 0">
            <td colspan="5" class="text-muted p-4">Pas de résultat</td>
          </tr>
        </tbody>
      </table>
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
import DateFormat from '../utils/DateFormat.js'
import { fr } from 'date-fns/locale'
import Datepicker from 'vue3-datepicker'
import TreeNode from './TreeNode.vue'

const formatDateTime = (date: Date | string): string => {
  const d = new Date(date)
  const day = String(d.getDate()).padStart(2, '0')
  const month = String(d.getMonth() + 1).padStart(2, '0')
  const year = d.getFullYear()
  const hours = String(d.getHours()).padStart(2, '0')
  const minutes = String(d.getMinutes()).padStart(2, '0')
  return `${day}/${month}/${year} ${hours}:${minutes}`
}

export default defineComponent({
  name: 'QuestionnaireFiles',
  props: {
    control: { type: Object, default: () => ({}) }
  },
  components: {
    InfoBar,
    Datepicker,
    TreeNode,
  },
  setup(props) {
    const store = useStore()

    const filter = ref('')
    const date_filter_start = ref<Date | ''>('')
    const date_filter_end = ref<Date | ''>('')
    const selected = ref<any[]>([])
    const repondantsListe = ref<any[]>([])
    const treeViewElements = ref<any[]>([])
    const localControl = ref<any | null>(null)

    const frLocale = fr
    const placeholder = 'jj/mm/aaaa'
    const format = 'dd/MM/yyyy'

    const accessibleControls = computed(() => store.state.controls)

    const getUsers = async () => {
      try {
        const resp = await axios.get(backendUrls.getDepositorsInControl(props.control.id))
        repondantsListe.value = Array.isArray(resp.data) ? resp.data : []
        console.log('repondantsListe après API:', repondantsListe.value)
        if (!repondantsListe.value.length) {
          repondantsListe.value = deriveRespondentsFromLocal()
          console.log('repondantsListe après deriveRespondentsFromLocal:', repondantsListe.value)
        }
      } catch (err) {
        repondantsListe.value = deriveRespondentsFromLocal()
        console.log('repondantsListe après erreur:', repondantsListe.value)
      }
    }

    const refreshFiles = async () => {
      try {
        const resp = await axios.get(backendUrls.getQuestionnaireAndThemesByCtlId(props.control.id))
        console.log('refreshFiles API response:', resp.data)
        localControl.value = resp.data.find((obj: any) => obj.id === props.control.id) || props.control
        console.log('localControl après API:', localControl.value)
      } catch (e) {
        console.log('refreshFiles erreur:', e)
        localControl.value = props.control
        console.log('localControl après erreur:', localControl.value)
      }
      const controlQuestionnaires = (localControl.value?.questionnaires || []).filter((q: any) => !q.is_draft)
      treeViewElements.value = getTreeViewElements(controlQuestionnaires)
      if (!repondantsListe.value.length) {
        repondantsListe.value = deriveRespondentsFromLocal()
        console.log('repondantsListe dans refreshFiles:', repondantsListe.value)
      }
    }

    const getTreeViewLevel = (
      item: any,
      questionnaireId: number | null = null,
      themeId: number | null = null,
      questionId: number | null = null,
      flags: {
        isAnnexe?: boolean
        isCorbeille?: boolean
        isPieceJointe?: boolean
        isFichierAnnexe?: boolean
        isFichierCorbeille?: boolean
        isFichierPieceJointe?: boolean
      } = {}
    ) => {
      const {
        isAnnexe = false,
        isCorbeille = false,
        isPieceJointe = false,
        isFichierAnnexe = false,
        isFichierCorbeille = false,
        isFichierPieceJointe = false,
      } = flags
      const maxLength = 100
      const obj: any = { name: '', short_name: '', dateDepot: '', repondant: '', _showChildren: true, _children: [], _id: '', id: '', url: '', order: 0, is_deleted: false }

      if (isAnnexe) {
        obj.name = 'Annexes'; obj._children = []; obj._id = 'annexes'; obj.id = `${questionnaireId}-annexes`
      } else if (isPieceJointe) {
        obj.name = 'Pièces jointes'; obj._children = []; obj._id = 'piecesjointes'; obj.id = `${questionnaireId}-piecesjointes`
      } else if (isCorbeille) {
        obj.name = 'Corbeille'; obj._children = []; obj._id = 'corbeille'; obj.id = `${questionnaireId}-corbeille`
      } else if (isFichierAnnexe) {
        obj.name = item.basename; obj.short_name = item.basename.length > maxLength ? item.basename.slice(0, maxLength) + '...' : item.basename; obj.url = item.url; obj._showChildren = false; obj._id = 'fileAnnexe'; obj.id = `${questionnaireId}-annexes-${item.id}`
      } else if (isFichierPieceJointe) {
        obj.name = item.basename; obj.short_name = item.basename.length > maxLength ? item.basename.slice(0, maxLength) + '...' : item.basename; obj.url = item.url; obj._showChildren = false; obj._id = 'filePieceJointe'; obj.id = `${questionnaireId}-piecesjointes-${item.id}`
      } else if (isFichierCorbeille) {
        obj.name = item.basename; obj.short_name = item.basename.length > maxLength ? item.basename.slice(0, maxLength) + '...' : item.basename; obj.dateDepot = formatDateTime(item.created); obj.repondant = `${item.author?.first_name ?? ''} ${item.author?.last_name ?? ''}`.trim(); obj.url = item.url; obj._showChildren = false; obj._id = 'fileCorbeille'; obj.id = `${questionnaireId}-corbeille-${item.id}`; obj.is_deleted = !!item.is_deleted
      } else if (questionId != null) {
        obj.name = item.basename; obj.short_name = item.basename.length > maxLength ? item.basename.slice(0, maxLength) + '...' : item.basename; obj.dateDepot = formatDateTime(item.created); obj.repondant = `${item.author?.first_name ?? ''} ${item.author?.last_name ?? ''}`.trim(); obj._id = 'file'; obj.id = `${questionnaireId}-${themeId}-${questionId}-${item.id}`; obj.url = item.url; obj.is_deleted = !!item.is_deleted
      } else if (themeId != null && questionId == null) {
        obj.name = `Question ${(item.order ?? 0) + 1} - ${item.title || item.description || ''}`; obj._children = []; obj._id = 'question'; obj.id = `${questionnaireId}-${themeId}-${item.id}`; obj.order = item.order ?? 0
      } else if (questionnaireId !== null && themeId === null) {
        obj.name = `Thème ${(item.order ?? 0) + 1} - ${item.title || item.description || ''}`; obj._children = []; obj._id = 'theme'; obj.id = `${questionnaireId}-${item.id}`; obj.order = item.order ?? 0
      } else {
        obj.name = `Questionnaire ${item.numbering ?? ''} - ${item.title || item.description || ''}`; obj._children = []; obj._id = 'questionnaire'; obj.id = item.id; obj.order = item.numbering ?? 0
      }
      return obj
    }

    const getTreeViewElements = (accessibleQuestionnaires: any[]) => {
      return (accessibleQuestionnaires || []).map((element: any) => {
        const objQuestionnaire = getTreeViewLevel(element)
        if (element.themes && element.themes.length) {
          objQuestionnaire._children = element.themes.map((theme: any) => {
            const objTheme = getTreeViewLevel(theme, element.id)
            if (theme.questions && theme.questions.length) {
              objTheme._children = theme.questions.map((question: any) => {
                const objQuestion = getTreeViewLevel(question, element.id, theme.id)
                if (question.response_files && question.response_files.length) {
                  objQuestion._children = question.response_files
                    .filter((rf: any) => rf.is_deleted === false)
                    .filter(filterByDate)
                    .map((rf: any) => getTreeViewLevel(rf, element.id, theme.id, question.id))
                  objQuestion._showChildren = true
                  ;(objQuestion as any)._selectable = true
                } else {
                  objQuestion._showChildren = false
                }
                return objQuestion
              })
            }
            return objTheme
          })
        }

        const objAnnexes = getTreeViewLevel(null, element.id, null, null, { isAnnexe: true })
        const objCorbeille = getTreeViewLevel(null, element.id, null, null, { isCorbeille: true })
        const objPiecesJointes = getTreeViewLevel(null, element.id, null, null, { isPieceJointe: true })

        objPiecesJointes._children = (accessibleQuestionnaires || [])
          .filter((aq: any) => aq.id === element.id)
          .flatMap((fq: any) => (fq.questionnaire_files || [])
            .filter(filterByDate)
            .flatMap((qf: any) => qf ? getTreeViewLevel(qf, element.id, null, null, { isFichierPieceJointe: true }) : []))

        objAnnexes._children = (accessibleQuestionnaires || [])
          .filter((aq: any) => aq.id === element.id)
          .flatMap((fq: any) => (fq.themes || [])
            .flatMap((t: any) => (t.questions || [])
              .flatMap((q: any) => (q.question_files || [])
                .filter(filterByDate)
                .flatMap((qf: any) => qf ? getTreeViewLevel(qf, element.id, null, null, { isFichierAnnexe: true }) : []))))

        objCorbeille._children = (accessibleQuestionnaires || [])
          .filter((aq: any) => aq.id === element.id)
          .flatMap((fq: any) => (fq.themes || [])
            .flatMap((t: any) => (t.questions || [])
              .flatMap((q: any) => (q.response_files || [])
                .filter((rf: any) => rf.is_deleted === true)
                .filter(filterByDate)
                .flatMap((rf: any) => rf ? getTreeViewLevel(rf, element.id, null, null, { isFichierCorbeille: true }) : []))))

        if (!objCorbeille._children.length) objCorbeille._showChildren = false
        else objQuestionnaire._children.unshift(objCorbeille)
        if (!objAnnexes._children.length) objAnnexes._showChildren = false
        else objQuestionnaire._children.unshift(objAnnexes)
        if (!objPiecesJointes._children.length) objPiecesJointes._showChildren = false
        else objQuestionnaire._children.unshift(objPiecesJointes)

        return objQuestionnaire
      })
    }

    const filterByDate = (responseFile: any) => {
      if (!responseFile.created) return false
      const creation_date = new Date(responseFile.created)
      if (!date_filter_start.value && !date_filter_end.value) return true
      if (date_filter_start.value && date_filter_end.value) return date_filter_start.value <= creation_date && creation_date <= date_filter_end.value
      if (date_filter_start.value) return date_filter_start.value <= creation_date
      if (date_filter_end.value) return creation_date <= date_filter_end.value
      return true
    }

    const pickFiles = (selected_id = '') => {
      const collectFilesRecursive = (node: any): any[] => {
        if (!node) return []
        if (node._id && node._id.startsWith('file')) return [node]
        const children = Array.isArray(node._children) ? node._children : []
        return children.flatMap(collectFilesRecursive)
      }
      
      const filterVal = filter.value
      return treeViewElements.value
        .flatMap(collectFilesRecursive)
        .filter((file: any) => !filterVal || file.repondant === filterVal)
        .filter((file: any) => !selected_id || file.id.startsWith(selected_id))
    }

    const pickFilesFiltered = () => pickFiles().filter((file: any) => filterByDate(file))

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
    const exportFiltered = () => zipFiles(pickFilesFiltered())

    const deriveRespondentsFromLocal = (): any[] => {
      const acc = new Map<string, any>()
      const lc: any = localControl.value
      const questionnaires: any[] = (lc?.questionnaires || [])
      questionnaires.forEach((q: any) => {
        (q.themes || []).forEach((t: any) => {
          (t.questions || []).forEach((qq: any) => {
            (qq.response_files || []).forEach((rf: any) => {
              const a = rf?.author; if (!a) return
              const key = String(a.id ?? `${a.first_name}-${a.last_name}`)
              if (!acc.has(key)) acc.set(key, { id: a.id, first_name: a.first_name || '', last_name: a.last_name || '' })
            })
          })
        })
        ;(q.themes || []).forEach((t: any) => {
          ;(t.questions || []).forEach((qq: any) => {
            ;(qq.response_files || []).filter((rf: any) => rf?.is_deleted).forEach((rf: any) => {
              const a = rf?.author; if (!a) return
              const key = String(a.id ?? `${a.first_name}-${a.last_name}`)
              if (!acc.has(key)) acc.set(key, { id: a.id, first_name: a.first_name || '', last_name: a.last_name || '' })
            })
          })
        })
      })
      return Array.from(acc.values())
    }

    const optionKey = (opt: any) => String(opt?.id ?? `${opt?.first_name}-${opt?.last_name}`)

    const toggleNode = (nodeId: string) => {
      const toggle = (node: any) => {
        if (node.id === nodeId) {
          node._showChildren = !node._showChildren
          return true
        }
        if (node._children) {
          for (const child of node._children) {
            if (toggle(child)) return true
          }
        }
        return false
      }
      for (const node of treeViewElements.value) {
        toggle(node)
      }
    }

    const selectNode = (node: any) => {
      if (node._id && node._id.startsWith('file')) {
        const idx = selected.value.findIndex((i) => i && i.id === node.id)
        if (idx === -1) {
          selected.value.push(node)
        } else {
          selected.value.splice(idx, 1)
        }
      }
    }

    onMounted(() => { getUsers(); refreshFiles() })

    return {
      filter, date_filter_start, date_filter_end, selected, repondantsListe, treeViewElements, frLocale, placeholder, format,
      accessibleControls,
      getUsers, refreshFiles, getTreeViewElements, filterByDate, pickFilesFiltered, pickFiles, zipFiles,
      exportSelected, exportFiltered, exportAll, toggleNode, selectNode, optionKey,
    }
  }
})
</script>

<style scoped>
.tree-table {
  width: 100%;
  border-collapse: collapse;
}

.tree-table thead {
  background-color: #f8f9fa;
  border-bottom: 2px solid #dee2e6;
  font-weight: bold;
}

.tree-table thead th {
  padding: 8px;
  text-align: left;
  border: none;
}

.tree-table tbody tr {
  border-bottom: 1px solid #e9ecef;
}

.tree-table tbody tr.selected {
  background-color: #f8f9fa;
}

.col-expand {
  width: 30px;
  padding: 0 8px !important;
}

.col-checkbox {
  width: 32px;
  padding: 0 8px !important;
}

.col-document {
  width: 550px;
  border-right: 1px solid #dee2e6;
  padding: 0 8px !important;
}

.col-date {
  width: 160px;
  border-right: 1px solid #dee2e6;
  padding: 0 8px !important;
}

.col-repondant {
  width: 150px;
  padding: 0 8px !important;
}
</style>
