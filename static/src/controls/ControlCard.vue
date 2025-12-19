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

<script>
import { defineComponent } from 'vue'
import ControlCreate from './ControlCreate'
import ControlTitle from './ControlTitle'
import QuestionnaireList from '../questionnaires/QuestionnaireList'
import UserSection from '../users/UserSection'
import ErrorBar from '../utils/ErrorBar'

export default defineComponent({
  props: {
    control: { type: Object, required: true },
    user: { type: Object, required: true },
    accessType: { type: String, default: '' },
  },
  computed: {
    noAccess() {
      // Vue 3: $parent chain is fragile, prefer prop or provide/inject, but keep for compatibility
      return this.$parent?.$parent?.noAccess ?? false
    },
  },
  components: {
    ControlCreate,
    ControlTitle,
    QuestionnaireList,
    UserSection,
    ErrorBar,
  },
})
</script>