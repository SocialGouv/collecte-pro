<template>
<div> <div class="card">
<div class="card-header">
 <h2 class="card-title">Etape 3 : Aperçu avant publication</h2>
</div>
<div class="card-body pb-6">
  <questionnaire-detail-for-preview v-bind:questionnaire="currentQuestionnaire">
 </questionnaire-detail-for-preview>
</div>
</div>
</div>
</template>

<script>
// Suppression de: import Vue from 'vue'
// Suppression de: import { mapFields } from 'vuex-map-fields'
import { mapState } from 'vuex' // Import de mapState de Vuex 4
import { defineComponent } from 'vue'

import QuestionnaireDetailForPreview from './QuestionnaireDetailForPreview'

export default defineComponent({ // Remplacement de Vue.extend
	computed: {
		// Remplacement de mapFields par mapState (Lecture seule)
		...mapState([
			'currentQuestionnaire',
		]),
	},
	components: {
		QuestionnaireDetailForPreview,
	},
})
</script>