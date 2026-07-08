<template>
  <div id="metadata" class="card">
    <div class="card-body">
      <div>
        <p class="with-line-breaks">{{ questionnaire.description }}</p>

        <p v-if="questionnaire.sent_date">
          <span class="fe fe-send" aria-hidden="true"></span>
          Date de transmission du questionnaire : {{ formatDate(questionnaire.sent_date) }}
        </p>
        <p v-if="questionnaire.end_date">
          <span class="fe fe-clock" aria-hidden="true"></span>
          Date de réponse souhaitée : {{ formatDate(questionnaire.end_date) }}
        </p>

        <questionnaire-file-list :files="questionnaire.questionnaire_files" :with-delete="false" />

        <div class="flex-row justify-content-end">
          <button v-if="!questionnaire.is_draft && accessType === 'demandeur'"
                  class="btn btn-secondary mx-2"
                  title="Modifier la date de réponse"
                  aria-label="Modifier la date de réponse"
                  data-toggle="modal"
                  data-target="#updateDateReponseModal">
            <span class="fe fe-edit mr-2"></span>
            <span class="mr-2">Modifier la date de réponse</span>
          </button>

          <div v-if="withTrash" class="mx-2">
            <a class="btn btn-secondary" :href="trashUrl" title="Aller à la corbeille">
              <span class="fe fe-trash-2 mr-2" aria-hidden="true"></span>Aller à la corbeille
            </a>
          </div>

          <button type="button"
                  class="btn btn-secondary dropdown-toggle dropdown-toggle-split mx-2"
                  data-toggle="dropdown"
                  aria-haspopup="true"
                  aria-expanded="false">
            <span class="fas fa-file-export mr-2" aria-hidden="true"></span>
            <span class="mr-2">Exporter</span>
          </button>

          <div class="dropdown-menu dropdown-menu-right">
            <div class="dropdown-header">Questionnaire</div>
            <a class="dropdown-item" :href="exportUrl" target="_blank" rel="noopener noreferrer" title="Format Word (.docx)">
              <span class="fe fe-file-text mr-2" aria-hidden="true"></span>Format Word (.docx)
            </a>

            <div v-if="!questionnaire.is_draft">
              <div class="dropdown-divider"></div>
              <div class="dropdown-header">Liste des réponses déposées</div>
              <a class="dropdown-item" :href="exportResponseFilesXlsxUrl" target="_blank" rel="noopener noreferrer" title="Format Excel (.xlsx)">
                <span class="far fa-file-excel mr-2" aria-hidden="true"></span>Format Excel (.xlsx)
              </a>
            </div>

            <div v-if="!questionnaire.is_draft">
              <div class="dropdown-divider"></div>
              <div class="dropdown-header">Export des fichiers</div>
              <a class="dropdown-item" href="#" @click.prevent="exportQuestionnaire">
                <span class="fas fa-file-export mr-2" aria-hidden="true"></span>Exporter (.zip)
              </a>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, computed } from 'vue'
import backendUrls from '../utils/backend'
import { saveAs } from 'file-saver'
import JSZip from 'jszip'
import JSZipUtils from 'jszip-utils'
import QuestionnaireFileList from './QuestionnaireFileList'

export default defineComponent({
  name: 'QuestionnaireMetadata',
  components: { QuestionnaireFileList },
  props: {
    questionnaire: { type: Object, required: true },
    control: { type: Object, required: true },
    withTrash: { type: Boolean, default: false },
    accessType: { type: String, default: '' },
  },
  setup(props) {
    const exportUrl = computed(() => {
      if (!props.questionnaire || props.questionnaire.id === undefined || props.questionnaire.id === null) {
        return '#'
      }
  return (backendUrls as any)['questionnaire-export'](props.questionnaire.id)
    })

    const exportResponseFilesXlsxUrl = computed(() => {
      if (!props.questionnaire || props.questionnaire.id === undefined || props.questionnaire.id === null) {
        return '#'
      }
  return (backendUrls as any)['responses-export'](props.questionnaire.id)
    })

    const trashUrl = computed(() => {
      if (!props.questionnaire || props.questionnaire.id === undefined || props.questionnaire.id === null) {
        return '#'
      }
  return (backendUrls as any).trash(props.questionnaire.id)
    })

    const formatDate = (date: string) => {
      const d = new Date(date)
      return d.toLocaleDateString()
    }

    const exportQuestionnaire = () => {
      const zip = new JSZip()
      const files: any[] = []

      props.questionnaire.themes?.forEach((theme: any) => {
        theme.questions?.forEach((q: any) => {
          q.response_files?.forEach((rf: any) => {
            if (rf) files.push({ ...rf, category: 'response_file', themeId: theme.order, questionId: q.order })
          })
          q.question_files?.forEach((qf: any) => {
            if (qf) files.push({ ...qf, category: 'question_file', themeId: theme.order, questionId: q.order })
          })
        })
      })

      const formatFilename = (file: any) => {
        const questionnaireNb = String(props.questionnaire.numbering).padStart(2, '0')
        const questionnaireId = `Q${questionnaireNb}`
        let themeId = ''
        let filename = ''
        if (file.category === 'question_file') {
          themeId = 'ANNEXES-AUX-QUESTIONS'
          filename = `Q${questionnaireNb}-${file.basename}`
        } else if (file.is_deleted) {
          themeId = 'CORBEILLE'
          filename = `Q${questionnaireNb}-${file.basename}`
        } else {
          themeId = 'T' + String(file.themeId + 1).padStart(2, '0')
          const questionId = String(file.questionId + 1).padStart(2, '0')
          filename = `Q${questionnaireNb}-${themeId}-${questionId}-${file.basename}`
        }
        return { questionnaireId, themeId, filename }
      }

      const exportFiles = files.filter(file => !file.is_deleted)
      let cnt = 0
      const zipFilename = props.control.reference_code + '.zip'
      if (exportFiles.length === 0) return

      exportFiles.forEach(file => {
        const url = window.location.origin + file.url
        JSZipUtils.getBinaryContent(url, (err: any, data: any) => {
          if (err) throw err
          const formatted = formatFilename(file)
          zip.folder(formatted.questionnaireId)
            ?.folder(formatted.themeId)
            ?.file(formatted.filename, data, { binary: true })

          cnt++
          if (cnt === exportFiles.length) zip.generateAsync({ type: 'blob' }).then(content => saveAs(content, zipFilename))
        })
      })
    }

    return {
      exportUrl,
      exportResponseFilesXlsxUrl,
      trashUrl,
      formatDate,
      exportQuestionnaire,
    }
  }
})
</script>
