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

<style scoped>
  .loader-container {
    text-align: center;
    z-index:9999;
    padding-top:100px;
    position:fixed;
    left:0;
    top:0;
    width:100%;
    height:100%;
    overflow:auto;
    background-color:rgba(0,0,0,.4);
  }
  .loader-wrapper {
    background-color:rgba(255,255,255,.9);
    width: 200px;
    margin: auto;
    padding: 6px;
    border-radius: 6px;
  }
  .loader {
    display: inline-block;
    position: relative;
    width: 80px;
    height: 80px;
  }
  .loader div {
    box-sizing: border-box;
    display: block;
    position: absolute;
    width: 64px;
    height: 64px;
    margin: 8px;
    border: 8px solid #6916a0;
    border-radius: 50%;
    animation: loader 1.2s cubic-bezier(0.5, 0, 0.5, 1) infinite;
    border-color: #6916a0 transparent transparent transparent;
  }
</style>
