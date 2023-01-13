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
  import Vue from 'vue'

  import ControlCreate from './ControlCreate'
  import ControlTitle from './ControlTitle'
  import QuestionnaireList from '../questionnaires/QuestionnaireList'
  import UserSection from '../users/UserSection'
  import ErrorBar from '../utils/ErrorBar'

  export default Vue.extend({
    props: [
      'control',
      'user',
      'accessType',
    ],
    computed: {
      noAccess() {
        return this.$parent.$parent.noAccess;
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
