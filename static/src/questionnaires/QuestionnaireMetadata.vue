<template>
  <div id="metadata" class="card">
    <div class="card-body">
      <div>
        <p class="with-line-breaks">{{ questionnaire.description }}</p>

        <p v-if="questionnaire.sent_date">
          <span class="fe fe-send" aria-hidden="true"></span>
          Date de transmission du questionnaire :
          {{ questionnaire.sent_date | DateFormat }}
        </p>
        <p v-if="questionnaire.end_date">
          <span class="fe fe-clock" aria-hidden="true"></span>
          Date de réponse souhaitée :
          {{ questionnaire.end_date | DateFormat }}
        </p>
        <p>
          <questionnaire-file-list :files="questionnaire.questionnaire_files" :with-delete="false">
          </questionnaire-file-list>
        </p>
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
            <a class="btn btn-secondary"
              :href="trashUrl"
              title="Aller à la corbeille">
              <span class="fe fe-trash-2 mr-2" aria-hidden="true"></span>Aller à la corbeille
            </a>
          </div>

          <button type="button"
                  class="btn btn-secondary dropdown-toggle dropdown-toggle-split mx-2"
                  data-toggle="dropdown"
                  aria-haspopup="true"
                  aria-expanded="false">
            <span class="fas fa-file-export mr-2" aria-hidden="true"></span>
            <span class="mr-2">
              Exporter
            </span>
          </button>
          <div class="dropdown-menu dropdown-menu-right">
            <div class="dropdown-header">Questionnaire</div>
            <a class="dropdown-item"
              :href="exportUrl"
              target="_blank"
              rel="noopener noreferrer"
              title="Format Word (.docx)">
              <span class="fe fe-file-text mr-2" aria-hidden="true"></span>Format Word (.docx)
            </a>
            <div v-if="!questionnaire.is_draft">
              <div class="dropdown-divider"></div>
              <div class="dropdown-header">Liste des réponses déposées</div>
              <a class="dropdown-item"
                :href="exportResponseFilesXlsxUrl"
                target="_blank"
                rel="noopener noreferrer"
                title="Format Excel (.xlsx)">
                <span class="far fa-file-excel mr-2" aria-hidden="true"></span>
                Format Excel (.xlsx)
              </a>
            </div>
            <div v-if="!questionnaire.is_draft">
              <div class="dropdown-divider"></div>
              <div class="dropdown-header">Export des fichiers</div>
              <a class="dropdown-item"
                href="#"
                @click="exportQuestionnaire"
              >
                <span class="fas fa-file-export mr-2" aria-hidden="true"></span>
                Exporter (.zip)
              </a>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
<script>
import backendUrls from '../utils/backend'
import DateFormat from '../utils/DateFormat.js'
import Vue from 'vue'

import JSZip from 'jszip'
import JSZipUtils from 'jszip-utils'
import { saveAs } from 'file-saver'

import QuestionnaireFileList from './QuestionnaireFileList'

export default Vue.extend({
  props: ['questionnaire', 'control', 'withTrash', 'accessType'],
  filters: {
    DateFormat,
  },
  components: {
    QuestionnaireFileList,
  },
  computed: {
    exportUrl() {
      return backendUrls['questionnaire-export'](this.questionnaire.id)
    },
    exportResponseFilesXlsxUrl() {
      return backendUrls['responses-export'](this.questionnaire.id)
    },
    trashUrl() {
      return backendUrls.trash(this.questionnaire.id)
    },
  },
  methods: {
    exportQuestionnaire() {
      this.$parent.$parent.loaderActive = true;

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

      let files = [this.questionnaire]
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
        [this.questionnaire]
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
        this.$parent.$parent.loaderActive = false;
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
              this.$parent.$parent.loaderActive = false;
              saveAs(content, zipFilename)
            })
          }
        })
      })
    },
  },
})

</script>
