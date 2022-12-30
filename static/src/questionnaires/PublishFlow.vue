<template>
  <modal-flow ref="modalFlow" :action-function="publishFunction">
    <template v-slot:confirm-modal-form>
      <div class="modal-header border-bottom-0">
        <div id="modal_title" class="modal-title">
          Vous y êtes presque ! En cochant ces mentions, vous êtes informés que :
        </div>
      </div>

      <div class="modal-body">
        <fieldset class="form-fieldset">
          <legend>Merci de cocher toutes les cases pour valider cette action</legend>
          <label for="checkModif" class="custom-control custom-checkbox">
            <input type="checkbox"
                   id="checkModif"
                    class="custom-control-input"
                    required>
            <span class="custom-control-label">
              Le questionnaire ne pourra plus être modifié
            </span>
          </label>
          <label for="checkVisible" class="custom-control custom-checkbox">
            <input type="checkbox"
                   id="checkVisible"
                    class="custom-control-input"
                    required>
            <span class="custom-control-label">
              Le questionnaire deviendra visible par l'organisme interrogé
            </span>
          </label>
          <label for="checkInfo" class="custom-control custom-checkbox">
            <input type="checkbox"
                   id="checkInfo"
                    class="custom-control-input"
                    required>
            <span class="custom-control-label">
              Vous devrez informer l'organisme interrogé
            </span>
          </label>
        </fieldset>
      </div>

      <div class="modal-footer border-top-0">
        <button type="button"
                class="btn btn-secondary"
                data-dismiss="modal"
                title="J'ai encore des modifications à faire"
        >
          <span class="fa fa-chevron-left mr-2" aria-hidden="true"></span>
          J'ai encore des modifications à faire
        </button>
        <button type="submit"
                class="btn btn-primary"
                title="Publier le questionnaire"
        >
          <span class="fa fa-rocket mr-1" aria-hidden="true"></span>
          Publier le questionnaire
        </button>
      </div>
    </template>

    <template v-slot:wait-message>
      Questionnaire en cours de publication ...
    </template>

    <template v-slot:error-message>
      <div>
        Le questionnaire n'a pas pu être publié. Vous pouvez réessayer.
      </div>
      <div>
        Si l'erreur persiste, vous pouvez contacter
        <a :href="'mailto:' + config.support_team_email +
                  '?subject=Erreur lors de la publication : ' +
                  $refs.modalFlow.error.message"
            class="text-nowrap"
            target="_blank"
            rel="noopener noreferrer"
        >
          {{ config.support_team_email }}
        </a>
        , et indiquer l'erreur suivante :
      </div>
      <div>
        {{ $refs.modalFlow.error.message }}
      </div>
    </template>

    <template v-slot:success-modal-body>
      <div class="modal-header border-bottom-0 flex-column align-items-center">
        <p>
          <span class="fe fe-check-circle fg-success big-icon" aria-hidden="true"></span>
        </p>
        <div id="modal_title" class="text-center">
          Bravo, votre questionnaire est publié!
        </div>
        <div class="mt-5">
            <p>Pensez à informer l'organisme interrogé.</p>
            <p>Si des réponses sont déposées par l'organisme interrogé, vous recevrez un email de
          notification.</p>
        </div>
      </div>
      <div class="modal-body text-center">
        <div class="mt-5 flex-row justify-content-center">
          <button type="button"
            class="btn btn-primary ml-2"
            @click="goHome"
          >
            <span class="fa fa-chevron-left mr-2" aria-hidden="true"></span>
            Revenir à l'accueil
          </button>
          <a class="btn btn-primary ml-2"
              :href="'mailto:' + emailHeader.audited +
                    '?cc=' + emailHeader.inspectors +
                    '&subject=' + emailSubject +
                    '&body=' + emailBody"
              target="_blank"
              rel="noopener noreferrer"
          >
            Créer un mail pour l'informer
          </a>
        </div>
      </div>
    </template>

  </modal-flow>
</template>

<script>
import axios from 'axios'
import backend from '../utils/backend'
import { mapFields } from 'vuex-map-fields'
import { mapState } from 'vuex'
import ModalFlow from '../utils/ModalFlow'
import Vue from 'vue'

export default Vue.extend({
  components: {
    ModalFlow,
  },
  data() {
    return {
      users: [],
    }
  },
  props: {
    questionnaire: Object,
    controlId: Number,
    publishFunction: Function,
    // Pass window dependency for testing
    window: {
      default: () => window,
    },
  },
  computed: {
    ...mapFields([
      'config',
    ]),
    ...mapState({
      controls: 'controls',
      config: 'config',
    }),
    emailSubject: function() {
      if (this.config.env_name != '' && !this.config.env_name.toLowerCase().startsWith("production")) {
        return this.config.env_name + ' - Questionnaire publié';
      }
      return 'Questionnaire publié';
    },
    emailHeader: function() {
      const uniq = (arrArg) => arrArg.filter((elem, pos, arr) => arr.indexOf(elem) === pos)
      const currentControl = this.controls.find(control => control.id === this.questionnaire.control)

      if (currentControl) {
        const inspectors = this.users.filter(u => u.profile_type === 'inspector').map(u => u.email).join(';')
        const audited = this.users.filter(u => u.profile_type === 'audited').map(u => u.email).join(';')
        return { inspectors, audited }
      }

      return {}
    },
    emailBody: function() {
      const newline = '%0d%0a'
      const currentControl = this.controls.find(control => control.id === this.questionnaire.control)
      const expiryDateString = this.questionnaire.end_date === null ? '' : `${newline}${newline}La date limite de réponse est le ${this.questionnaire.end_date}.`

      if (currentControl) {
        return `Bonjour,${newline}${newline}Un nouveau questionnaire vient d'être ajouté à la procédure « ${currentControl.title} ». Il s'agit du questionnaire numéro ${this.questionnaire.numbering} : ${this.questionnaire.title}.${expiryDateString}${newline}${newline}Nous vous invitons à vous connecter à collecte-pro pour le consulter et apporter vos réponses : ${this.config.site_url}${newline}${newline}Cordialement,`
      }

      return ''
    },
  },
  methods: {
    getUsers() {
      axios.get(backend.getUsersInControl(this.controlId))
        .then((response) => {
          this.users = response.data
        })
    },
    start() {
      console.debug('outer start!')
      this.$refs.modalFlow.start()
    },
    goHome() {
      setTimeout(() => {
        this.window.location.href = backend["control-detail"](
          this.questionnaire.control
        );
      }, 500);
    },
  },
  mounted() {
    this.getUsers()
  },
})
</script>

<style scoped>

</style>
