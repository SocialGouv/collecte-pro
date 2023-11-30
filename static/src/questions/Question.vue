<template>
  <div class="card-header border-0 p-0">
    <span class="stamp stamp-md bg-blue mr-3 cursor-pointer">
      {{ themeNumbering }}.{{ questionNumbering }}
    </span>

    <div class="card-text cursor-pointer">
      <button type="button" class="btn btn-secondary no-border question">{{ question.description}}</button>
      <div class="tags">
        <template v-if="questionFileCount > 0">
          <button
            type="button"
            class="btn tag tag-orange pull-left btn-file"
          >
            {{ questionFileCount }} fichier{{ questionFileCount === 1 ? '': 's' }}
            annexe{{ questionFileCount === 1 ? '': 's' }}
            <span class="tag-addon">
              <span class="fe fe-paperclip" aria-hidden="true"></span>
            </span>
          </button>
        </template>
        <template v-if="responseFileCount">
          <button
            type="button"
            class="btn tag tag-azure pull-left btn-file"
          >
            {{ responseFileCount }} fichier{{ responseFileCount === 1 ? '': 's' }}
            déposé{{ responseFileCount === 1 ? '': 's' }}
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
import '../../css/questions.css'
import Vue from 'vue'

import EventBus from '../events'

export default Vue.extend({
  props: {
    themeNumbering: Number,
    questionNumbering: Number,
    question: Object,
  },
  data() {
    return {
      questionFileCount: 0,
      responseFileCount: 0,
    }
  },
  mounted() {
    const numNotDeleted = files => files.filter(file => !file.is_deleted).length
    this.responseFileCount = 0
    if (this.question.response_files) {
      this.responseFileCount = numNotDeleted(this.question.response_files)
    }
    if (this.question.question_files) {
      this.questionFileCount = this.question.question_files.length
    }
    EventBus.$on('response-files-updated-' + this.question.id, responseFiles => {
      this.responseFileCount = numNotDeleted(responseFiles)
    })
  },
})
</script>
