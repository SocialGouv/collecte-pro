<template>
  <div class="page-main flex-row">
    <aside id="sidebar-vm" class="border-right">
      <sidebar />
    </aside>

    <main class="mt-3 mt-md-5 flex-grow-1 ml-6 ie-flex-row-child" role="main">
      <span id="contenu" class="sr-only">Début du contenu principal</span>

      <div v-if="loaderActive" class="loader-container">
        <div class="loader-wrapper">
          <div class="loader"></div>
          <p>Téléchargement en cours</p>
        </div>
      </div>

      <questionnaire-detail-page
        :control-id="controlId"
        :questionnaire-id="questionnaireId"
      />
    </main>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, provide } from 'vue'
import QuestionnaireDetailPage from './QuestionnaireDetailPage.vue'
import Sidebar from '../utils/Sidebar.vue'
import '../../css/questionnaires.css'

export default defineComponent({
  name: 'QuestionnaireDetail',
  components: {
    QuestionnaireDetailPage,
    Sidebar,
  },
  props: {
    controlId: { type: Number, required: true },
    questionnaireId: { type: Number, required: true },
  },
  setup() {
    const loaderActive = ref(false)
    provide('loaderActive', loaderActive)

    return { loaderActive }
  },
})
</script>
