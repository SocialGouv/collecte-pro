<template>
  <div class="modal" tabindex="-1" role="dialog">
    <div class="modal-dialog large-modal" role="document">
      <div class="modal-content">
        <div class="modal-header border-bottom-0" aria-labelledby="modal_title">
          <span class="fa fa-exchange-alt mr-2 mt-3" aria-hidden="true"></span>
          <div id="modal_title" class="modal-title">
            <div class="modal-title">Obtenir les droits de rédaction du questionnaire</div>
          </div>
          <button type="button"
                  class="close"
                  data-dismiss="modal"
                  aria-label="Fermer">
                  <span class="sr-only">Fermer</span>
          </button>
        </div>

        <div class="modal-body">
          <div class="row row-cards row-deck">
            <div class="col">
              <div class="card">
                <div class="card-body" v-if="questionnaire.editor">
                  <h4 class="mb-0">Contactez votre collègue {{ questionnaire.editor.first_name }} {{ questionnaire.editor.last_name }}</h4>
                  (<a :href="'mailto:' + questionnaire.editor.email">{{ questionnaire.editor.email }}</a>)
                  <p class="mt-4">Pour modifier ce questionnaire, votre collègue doit vous transférer les droits.</p>
                </div>
                <img :src="'/static/img/call-for-help.png'" alt="appel à l'aide">
              </div>
            </div>
            <div class="col">
              <div class="card">
                <div class="card-body">
                  <h4>Votre collègue n'est pas disponible ?</h4>
                  <p>Vous pouvez forcer le transfert des droits.</p>
                  <div class="alert alert-icon alert-danger" role="alert">
                    <span class="fe fe-alert-triangle mr-2" aria-hidden="true"></span>
                    Attention, dans ce cas toute modification non enregistrée par votre collègue sera perdue.
                  </div>
                  <div class="mb-4" v-if="questionnaire.modified_date">
                    Dernier enregistrement de ce questionnaire :
                    <br />{{ questionnaire.modified_date }} à
                    {{  questionnaire.modified_time }}
                  </div>
                  <button type="submit"
                    class="btn btn-primary"
                    title="Forcer le transfert des droits..."
                    @click="requestEditor()">
                    <span class="fa fa-exchange-alt mr-1" aria-hidden="true"></span>
                    Forcer le transfert des droits...
                  </button>
                </div>
              </div>
            </div>
          </div>

          <contact-support></contact-support>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import '../../css/editors.css'
import ContactSupport from '../utils/ContactSupport'
import Vue from 'vue'
import Vuex from 'vuex'

Vue.use(Vuex)

export default Vue.extend({
  props: ['questionnaire'],
  methods: {
    requestEditor() {
      this.$emit('request-editor')
    },
  },
  components: {
    ContactSupport,
  },
})
</script>



