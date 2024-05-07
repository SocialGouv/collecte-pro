<template>
  <div class="page-main flex-row">
    <div id="sidebar-vm" class="border-right">
      <sidebar></sidebar>
    </div>
    <main class="mt-3 mt-md-5 flex-grow-1 ml-6 ie-flex-row-child" role="main">
      <a name="contenu"> </a>
      <div
        v-if="this.loaderActive"
        class="loader-container"
      >
        <div class="loader-wrapper">
          <div class="loader"></div>
          <p>Téléchargement en cours</p>
        </div>
      </div>
      <questionnaire-detail-page :control-id="controlId" :questionnaire-id="questionnaireId">
      </questionnaire-detail-page>
    </main>
  </div>
</template>

<script>
import '../../css/questionnaires.css'
import QuestionnaireDetailPage from './QuestionnaireDetailPage'
import Sidebar from '../utils/Sidebar'
import Vue from 'vue'

export default Vue.extend({
  name: 'QuestionnaireDetail',
  props: {
    controlId: Number,
    questionnaireId: Number,
  },
  data: function() {
    return {
      loaderActive: false,
    }
  },
  components: {
    QuestionnaireDetailPage,
    Sidebar,
  },
})
</script>


