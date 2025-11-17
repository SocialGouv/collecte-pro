<template>
  <div :id="'question' + themeNumbering + '-' + questionNumbering"
       class="card m-0 p-0 pb-0">
    <div class="card-header border-0"
         :data-bs-toggle="collapseValue"
         :data-bs-target="'#question-body-' + question.id">
      <Question :theme-numbering="themeNumbering"
                :question-numbering="questionNumbering"
                :question="question" />
    </div>
    <div :class="collapseValue" :id="'question-body-' + question.id">
      <slot></slot>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, computed } from 'vue'
import Question from './Question'

interface QuestionType {
  id: number
  description: string
  question_files?: any[]
  response_files?: any[]
}

export default defineComponent({
  name: 'QuestionBoxWrapper',
  components: { Question },
  props: {
    question: { type: Object as () => QuestionType, required: true },
    questionNumbering: { type: Number, required: true },
    themeNumbering: { type: Number, required: true },
    withCollapse: { type: Boolean, default: false },
  },
  setup(props) {
    const collapseValue = computed(() => (props.withCollapse ? 'collapse' : ''))
    return { collapseValue }
  },
})
</script>
