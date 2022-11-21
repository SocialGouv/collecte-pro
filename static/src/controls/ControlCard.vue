<template>
  <div>
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

  export default Vue.extend({
    props: [
      'control',
      'user',
      'accessType',
    ],
    components: {
      ControlCreate,
      ControlTitle,
      QuestionnaireList,
      UserSection,
    },
  })
</script>