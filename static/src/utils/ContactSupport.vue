<template>
  <div class="card">
    <div class="card-body alert alert-info" role="alert">
      <div class="mb-4">
        <h4><span class="fe fe-help-circle mr-1" aria-hidden="true"></span>Un problème, une question ?</h4>
        Nous sommes là pour vous aider. N'hésitez pas à prendre contact avec l'équipe collecte-pro !
      </div>
      <a role="button"
         :href="'mailto:' + config.support_team_email"
         class="btn btn-primary"
         title="Contacter le support collecte-pro">
        <span class="fe fe-mail mr-1" aria-hidden="true"></span>
        Contacter le support collecte-pro
      </a>
    </div>
  </div>
</template>

<script>
import { mapFields } from 'vuex-map-fields'
import Vue from 'vue'
import Vuex from 'vuex'

Vue.use(Vuex)

export default Vue.extend({
  computed: {
    ...mapFields(['config']),
  },
})

</script>
