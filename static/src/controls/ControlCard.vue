<template>
  <div>
    <error-bar v-if="noAccess">
        <p>L'espace de dépôt demandé n'est pas accessible. Vous avez été redirigé vers le premier espace de dépôt qui vous est accessible.</p>
    </error-bar>
    <control-title :control="control" :accessType="accessType"></control-title>
    <questionnaire-list :control="control" :user="user" :accessType="accessType">
    </questionnaire-list>
    <user-section :control="control" :accessType="accessType"></user-section>
  </div>

</template>

<script lang="ts">
import { defineComponent } from 'vue'
import ControlCreate from './ControlCreate.vue'
import ControlTitle from './ControlTitle.vue'
import QuestionnaireList from '../questionnaires/QuestionnaireList.vue'
import UserSection from '../users/UserSection.vue'
import ErrorBar from '../utils/ErrorBar.vue'

export default defineComponent({
  name: 'ControlCard',
  props: {
    control: { type: Object, required: true },
    user: { type: Object, required: true },
    accessType: { type: String, default: '' },
  },
  components: {
    ControlCreate,
    ControlTitle,
    QuestionnaireList,
    UserSection,
    ErrorBar,
  },
  computed: {
    noAccess(): boolean {
      // En Vue 3, $parent existe toujours mais le typage TS nécessite un cast
      return (this.$parent?.$parent as any)?.noAccess ?? false
    },
  },
})
</script>
