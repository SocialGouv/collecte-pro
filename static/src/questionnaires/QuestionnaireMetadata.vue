<template>
  <div id="metadata" class="card">
    <div class="card-body">
      <div>
        <p class="with-line-breaks">{{ questionnaire.description }}</p>

        <p v-if="questionnaire.sent_date">
          <i class="fe fe-send" aria-hidden="true"></i>
          Date de transmission du questionnaire :
          {{ questionnaire.sent_date | DateFormat }}
        </p>
        <p v-if="questionnaire.end_date">
          <i class="fe fe-clock" aria-hidden="true"></i>
          Date de réponse souhaitée :
          {{ questionnaire.end_date | DateFormat }}
        </p>
        <div class="flex-row justify-content-end">
          <div v-if="withTrash" class="mx-2">
            <a class="btn btn-secondary"
              :href="trashUrl"
              title="Aller à la corbeille">
              <i class="fe fe-trash-2 mr-2" aria-hidden="true"></i>Aller à la corbeille
            </a>
          </div>

          <button type="button"
                  class="btn btn-secondary dropdown-toggle dropdown-toggle-split mx-2"
                  data-toggle="dropdown"
                  aria-haspopup="true"
                  aria-expanded="false">
            <i class="fas fa-file-export mr-2" aria-hidden="true"></i>
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
              <i class="fe fe-file-text mr-2" aria-hidden="true"></i>Format Word (.docx)
            </a>
            <div v-if="!questionnaire.is_draft">
              <div class="dropdown-divider"></div>
              <div class="dropdown-header">Liste des réponses déposées</div>
              <a class="dropdown-item"
                :href="exportResponseFilesXlsxUrl"
                target="_blank"
                rel="noopener noreferrer"
                title="Format Excel (.xlsx)">
                <i class="far fa-file-excel mr-2" aria-hidden="true"></i>
                Format Excel (.xlsx)
              </a>
            </div>
            <div v-if="!questionnaire.is_draft">
              <div class="dropdown-divider"></div>
              <div class="dropdown-header">Export des fichiers</div>
              <a class="dropdown-item"
                href="#"
                @click="exportQuestionnaire()"
              >
                <i class="fas fa-file-export mr-2" aria-hidden="true"></i>
                Exporter (.zip)
              </button>
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

export default Vue.extend({
  props: ['questionnaire', 'control', 'withTrash'],
  filters: {
    DateFormat,
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
