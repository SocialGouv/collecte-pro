<template>
  <div class="preview">
    <questionnaire-metadata :questionnaire="questionnaire" />

    <div>
      <theme-box
        v-for="(theme, themeIndex) in questionnaire.themes"
        :key="theme.id"
        :theme="theme"
        :theme-numbering="themeIndex + 1"
      >
        <question-box
          v-for="(question, qIndex) in theme.questions"
          :key="question.id"
          :theme-numbering="themeIndex + 1"
          :question-numbering="qIndex + 1"
          :question="question"
        >
          <question-file-list :files="question.question_files" />
        </question-box>
      </theme-box>
    </div>
  </div>
</template>

<script>
import { defineComponent } from 'vue'
import QuestionBox from '../questions/QuestionBox.vue'
import QuestionFileList from '../questions/QuestionFileList.vue'
import QuestionnaireMetadata from './QuestionnaireMetadata.vue'
import ThemeBox from '../themes/ThemeBox.vue'

export default defineComponent({
  name: 'QuestionnairePreview',
  props: {
    questionnaire: {
      type: Object,
      required: true,
    },
  },
  components: {
    QuestionBox,
    QuestionFileList,
    QuestionnaireMetadata,
    ThemeBox,
  },
})
</script>
