<template>
  <div class="card-header border-0 p-0">
    <span class="stamp stamp-md bg-blue mr-3 cursor-pointer">
      {{ themeNumbering }}.{{ questionNumbering }}
    </span>

    <div class="card-text cursor-pointer">
      <button type="button" class="btn btn-secondary no-border question">
        {{ question.description }}
      </button>
      <div class="tags">
        <template v-if="questionFileCount > 0">
          <button type="button" class="btn tag tag-orange pull-left btn-file">
            {{ questionFileCount }} fichier{{ questionFileCount === 1 ? '' : 's' }}
            annexe{{ questionFileCount === 1 ? '' : 's' }}
            <span class="tag-addon">
              <span class="fe fe-paperclip" aria-hidden="true"></span>
            </span>
          </button>
        </template>
        <template v-if="responseFileCount">
          <button type="button" class="btn tag tag-azure pull-left btn-file">
            {{ responseFileCount }} fichier{{ responseFileCount === 1 ? '' : 's' }}
            déposé{{ responseFileCount === 1 ? '' : 's' }}
            <span class="tag-addon">
              <span class="fe fe-file" aria-hidden="true"></span>
            </span>
          </button>
        </template>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted, watch } from 'vue'
import EventBus from '../events'
import '../../css/questions.css'

export default defineComponent({
  name: 'Question',
  props: {
    themeNumbering: { type: Number, required: true },
    questionNumbering: { type: Number, required: true },
    question: { type: Object as () => any, required: true },
  },
  setup(props) {
    const questionFileCount = ref(0)
    const responseFileCount = ref(0)

    const numNotDeleted = (files: any[]) => files.filter(f => !f.is_deleted).length

    onMounted(() => {
      if (props.question.response_files) {
        responseFileCount.value = numNotDeleted(props.question.response_files)
      }
      if (props.question.question_files) {
        questionFileCount.value = props.question.question_files.length
      }

      EventBus.$on('response-files-updated-' + props.question.id, (responseFiles: any[]) => {
        responseFileCount.value = numNotDeleted(responseFiles)
      })
    })

    return {
      questionFileCount,
      responseFileCount,
    }
  },
})
</script>
