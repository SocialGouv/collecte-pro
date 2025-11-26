<template>
<div class="modal fade add-user-modal" id="addUserModal" tabindex="-1" role="dialog" aria-labelledby="modal_title" aria-hidden="true" aria-modal="true">
  <div class="modal-dialog" role="document">
    <div class="modal-content">
      <div class="modal-header">
        <div id="modal_title" class="modal-title">{{ editingControl.title }}</div>
      </div>
      <div class="modal-body">
        <div v-if="hasErrors" class="alert alert-danger" role="alert">
          L'ajout d'utilisateur n'a pas fonctionné. Vous pouvez réessayer.
        </div>
        <div v-if="editingProfileType==='inspector'" class="text-center">
          <h4><span class="fa fa-university mr-2" aria-hidden="true"></span><strong>Équipe d'instruction</strong></h4>
        </div>
        <div v-if="editingProfileType==='audited'" class="text-center">
          <h4><span class="fa fa-building mr-2" aria-hidden="true"></span><strong>Organisme interrogé</strong></h4>
        </div>

        <info-bar>
          <p>Tous les champs sont obligatoires.</p>
        </info-bar>
        <form @submit.prevent="validateEmail" v-if="stepShown === 1" @keydown.esc="resetFormData">
          <div class="form-fieldset">
            <div class="form-group">
              <label id="email-label" class="form-label" for="email">
                Email
                <span class="form-required">*</span>
              </label>
              <input id="email"
                     type="email"
                     autocapitalize=off
                     autocorrect=off
                     class="form-control"
                     v-bind:class="{ 'state-invalid': errors.email }"
                     v-model="formData.email"
                     placeholder="prenom.nom@example.org"
                     required
                     aria-labelledby="email-label"
                     aria-describedby="erreur-email">
            </div>
            <div class='form-group'>
              <label id="email-confirm-label" class="form-label" for="confirm_email">
                Confirmer l'Email
                <span class="form-required">*</span>
              </label>
              <input id="confirm_email"
                     type="email"
                     autocapitalize=off
                     autocorrect=off
                     class="form-control"
                     v-bind:class="{ 'state-invalid': errors.email }"
                     v-model="formData.email_confirm"
                     placeholder="prenom.nom@example.org"
                     required
                     aria-labelledby="email-confirm-label"
                     aria-describedby="erreur-email">
              <p class="text-muted pl-2" v-if="errors.email" id="erreur-email">
                <span class="fa fa-warning" aria-hidden="true"></span>
                {{ errors.email.join(' / ')}}
              </p>
            </div>
          </div>
          <div class="flex-row justify-content-between">
            <button type="button" class="btn btn-secondary" @click="cancel">
              <span class="fa fa-times mr-2" aria-hidden="true"></span>
              Annuler
            </button>
            <button type="submit" class="btn btn-primary">
              Suivant
              <span class="fa fa-chevron-right ml-2" aria-hidden="true"></span>
            </button>
          </div>
        </form>

        <form @submit.prevent="findUser" v-if="stepShown === 1.5" @keydown.esc="resetFormData">
          <div class="alert alert-warning alert-icon my-8" role="alert">
            <span class="fa fa-exclamation-circle mr-2" aria-hidden="true" ></span>
            <div class="mb-4">
              Vous allez ajouter
              <strong>{{ formData.email }}</strong>
              comme
              <strong>Demandeur</strong>
              .
            </div>
            <div> Cet email ne finit pas par
            <template v-for="(ending, index) in expectedEndingsArray" :key="index">
              <strong>{{ ending }}</strong>
              <span v-if="index < expectedEndingsArray.length - 2">,</span>
              <span v-if="index === expectedEndingsArray.length - 2" class="mr-1">ou</span>
            </template>
            .
          </div>
          </div>
          <div class="flex-row justify-content-between">
            <button type="button" class="btn btn-secondary" @click="cancel">
              <span class="fa fa-times mr-2" aria-hidden="true"></span>
              Annuler
            </button>
            <div class="text-right">
              <button type="button" class="btn btn-secondary" @click="back">
                C'est une erreur,<br/>
                <span class="fa fa-chevron-left mr-2" aria-hidden="true"></span>
                Retour
              </button>
              <button type="submit" class="btn btn-primary">
                C'est volontaire,<br/>Suivant
                <span class="fa fa-chevron-right ml-2" aria-hidden="true"></span>
              </button>
            </div>
          </div>
        </form>

        <form @submit.prevent="addUser" v-if="stepShown === 2" @keydown.esc="resetFormData">
          <div class="form-fieldset">
            <p class="form-label">Email : {{ formData.email}}</p>
          </div>
          <div v-if="foundUser" class="form-fieldset">
            <p class="form-label">Prénom : {{ formData.first_name}}</p>
            <p class="form-label">Nom : {{ formData.last_name}}</p>
          </div>
          <fieldset v-else class="form-fieldset">
            <div class="form-group">
              <label class="form-label" for="prenom">Prénom<span class="form-required"></span></label>
              <input id="prenom" type="given-name" class="form-control" v-bind:class="{ 'state-invalid': errors.first_name }" v-model="formData.first_name" placeholder="prenom" required>
              <p class="text-muted pl-2" v-if="errors.first_name"><span class="fa fa-warning" aria-hidden="true"></span> {{ errors.first_name.join(' / ')}}</p>
            </div>
            <div class="form-group">
              <label class="form-label" for="nom">Nom<span class="form-required"></span></label>
              <input id="nom" type="family-name" class="form-control" v-bind:class="{ 'state-invalid': errors.last_name }" v-model="formData.last_name" placeholder="nom" required>
              <p class="text-muted pl-2" v-if="errors.last_name"><span class="fa fa-warning" aria-hidden="true"></span> {{ errors.last_name.join(' / ')}}</p>
            </div>
          </fieldset>
          <div class="flex-row justify-content-between">
            <button type="button" class="btn btn-secondary" @click="cancel">
              <span class="fa fa-times mr-2" aria-hidden="true"></span>
              Annuler
            </button>
            <div class="text-right">
              <button type="button" class="btn btn-secondary" @click="back">
                <span class="fa fa-chevron-left mr-2" aria-hidden="true"></span>
                Retour
              </button>
              <button type="submit" class="btn btn-primary">Ajouter</button>
            </div>
          </div>
        </form>

        <div v-if="stepShown === 3" class="flex-column align-items-center">

          <div class="flex-row align-items-center">
            <span class="fe fe-check-circle fg-success big-icon mr-4" aria-hidden="true"></span>
            <h4 class="mb-0"> Utilisateur ajouté</h4>
          </div>

          <div class="mt-5">
            Vous avez ajouté {{ this.postResult.first_name }} {{ this.postResult.last_name }}.
          </div>

          <div class="mt-5">
            Pensez à l'informer qu'elle.il pourra désormais se connecter avec son email.
          </div>

          <div class="mt-5 flex-row justify-content-end">
            <button type="button" class="btn btn-secondary" @click="cancel">
              Je l'ai informé.e
            </button>
            <a class="btn btn-primary ml-2"
               :href="'mailto:' + postResult.email +
                      '?subject=' + emailSubject +
                      '&body=' + emailBody"
               target="_blank"
               rel="noopener noreferrer"
            >
              Créer un mail pour l'informer
            </a>
          </div>
        </div>
      </div>
    </div>
  </div>
</div>
</template>

<script lang="ts">
// Suppression de: import { mapFields } from 'vuex-map-fields'
import { mapState } from 'vuex'
import { defineComponent } from 'vue'
import axios from 'axios'
import backend from '../utils/backend'
// Suppression des imports/initialisations Vue 2: import Vue from 'vue', import { store } from '../store'
import InfoBar from '../utils/InfoBar.vue'
import EventBus from '../events'

axios.defaults.xsrfCookieName = 'csrftoken'
axios.defaults.xsrfHeaderName = 'X-CSRFTOKEN'

export default defineComponent({ // Remplacement de Vue.extend
  data() {
    return {
      formData: {
        first_name: '',
        last_name: '',
        email: '',
        email_confirm: '',
        control: '',
        profile_type: '',
      },
      postResult: [],
      errors: [],
      hasErrors: false,
      searchResult: {},
      foundUser: false,
      stepShown: 1,
      expectedEndingsArray: [],
    }
  },
  computed: {
    // Remplacement de mapFields par mapState pour les champs de lecture seule (y compris ceux de la configuration)
    ...mapState([
      'editingControl',
      'editingProfileType',
      // Nous récupérons l'objet config complet pour accéder aux sous-champs
      'config', 
    ]),
    
    // Remplacement des champs imbriqués de mapFields par des getters locaux sur l'objet 'config'
    expected_inspector_email_endings: function() {
      // Accès direct à la sous-propriété de l'état 'config'
      return this.config?.expected_inspector_email_endings || '';
    },
    site_url: function() {
      // Accès direct à la sous-propriété de l'état 'config'
      return this.config?.site_url || '';
    },
    // Le champ 'config' natif est déjà présent via mapState

    // Les computed methods pour l'emailSubject et emailBody sont conservées
    emailSubject: function() {
      if (this.config.env_name != '' && !this.config.env_name.toLowerCase().startsWith("production")) {
        return this.config.env_name + ' - Bienvenue sur collecte-pro';
      }
      return 'Bienvenue sur collecte-pro';
    },
    emailBody: function() {
      if (this.stepShown !== 3) {
        return ''
      }

      const newline = '%0d%0a'
      const body = 'Bonjour ' + this.postResult.first_name + ' ' + this.postResult.last_name + ',' +
        newline + newline + 'Je viens de vous ajouter à la procédure "' +
        this.editingControl.title +
        '" pour l\'organisme "' +
        this.editingControl.depositing_organization +
        '", en tant que membre de ' +
        (this.editingProfileType === 'inspector'
          ? 'l\'équipe d\'instruction.'
          : 'l\'organisme contrôlé.') +
        newline + newline +
        'Pour vous connecter, rendez-vous sur le site de collecte-pro :' +
        newline + newline +
        this.site_url + // Utilise le getter local migré
        newline + newline +
        'Cordialement,'

      return body
    },
  },
  components: {
    InfoBar,
  },
  methods: {
    cancel() {
      this.resetFormData()
      $('#addUserModal').modal('hide')
    },
    resetFormData() {
      this.formData = {
        first_name: '',
        last_name: '',
        email: '',
        email_confirm: '',
        control: '',
        profile_type: '',
      }
      this.stepShown = 1
      this.foundUser = false
      this.hasErrors = false
      this.errors = []
    },
    back() {
      switch (this.stepShown) {
        case 1.5:
          this.stepShown = 1
          break
        case 2:
          this.stepShown = 1
          break
        case 3:
          this.stepShown = 2
          break
        default:
          break
      }
    },
    validateEmail() {
      let expectedEndingsArray = [];
      const isInspectorEmail = email => {
          // At least one ending should match.
          // Utilise le getter local migré `this.expected_inspector_email_endings`
          const endingsString = this.expected_inspector_email_endings;

          // Si pas de fins d'emails attendues, on considère que c'est bon
          if (!endingsString) return true; 

          expectedEndingsArray = endingsString.split(',');
          this.expectedEndingsArray = expectedEndingsArray; // Met à jour data() pour l'affichage (étape 1.5)

          return expectedEndingsArray.some(ending => {
            return email.endsWith(ending)
          })
      }

      if (this.formData.email !== this.formData.email_confirm) {
        this.hasErrors = true;
        this.errors.email = ['Les deux champs e-mail doivent correspondre.'];
      } else if (this.editingProfileType === 'inspector' && !isInspectorEmail(this.formData.email)) {
        // expectedEndingsArray est déjà mis à jour dans isInspectorEmail
        this.stepShown = 1.5;
      } else {
        this.hasErrors = false;
        this.findUser();
      }
    },
    addUser() {
      this.formData.control = this.editingControl.id
      this.formData.profile_type = this.editingProfileType
      this.formData.email = this.formData.email.toLowerCase()
      
      // Ici, on envoie le contenu de `formData` (qui est local au composant), 
      // donc aucune mutation n'est nécessaire pour cette étape.
      axios.post(backend.user(), this.formData)
        .then(response => {
          this.postResult = response.data
          EventBus.$emit('users-changed', this.postResult)
          this.stepShown = 3
        })
        .catch((error) => {
          this.hasErrors = true
          this.errors = error.response.data
        })
    },
    findUser() {
      this.formData.email = this.formData.email.toLowerCase()
      axios.get(backend.user(), {
        params: {
          search: this.formData.email,
        },
      })
        .then(response => {
          this.searchResult = response.data
          if (response.data.length) {
            this.foundUser = true
            // Mise à jour de formData local
            Object.assign(this.formData, response.data[0])
          }
          this.stepShown = 2
        })
    },
  }
})
</script>