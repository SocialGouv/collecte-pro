<template>
<confirm-modal title="Réorganiser les thèmes du questionnaire"
               icon-class="fa fa-exchange-alt fa-rotate-90"
               confirm-button="Terminer"
               no-close="true"
               aria-describedby="reorganize-themes-title"
               @confirm="handleConfirm"
               >
  <error-bar v-if="errorMessage !== undefined" noclose="true">
    <p>{{ errorMessage }}</p>
  </error-bar>
  <div class="table-responsive border">
    <table class="table card-table" role="presentation">
      <transition-group name="theme-list" tag="tbody">
        <tr v-for="(theme, themeIndex) in themes"
            :id="'move-themes-modal-theme-' + themeIndex"
            :key="theme.id || themeIndex"
            class="flex-row">
          <td>
            <div class="flex-column align-items-center"> 
              <button :disabled="themeIndex === 0"
                      class="btn btn-secondary btn-sm move-up-button"
                      role="button"
                      type="button"
                      :aria-label="`Déplacer le thème '${theme.title}' vers le haut`"
                      title="Déplacer le thème vers le haut"
                      @click="moveThemeUp(themeIndex)">
                <span class="fa fa-chevron-up" aria-hidden="true"></span>
                <span class="sr-only">Vers le haut</span>
              </button>
              <div aria-live="polite" class="sr-only">{{ themeIndex + 1 }}</div>
              <button :disabled="themeIndex === (themes.length - 1)"
                      class="btn btn-secondary btn-sm move-down-button"
                      role="button"
                      type="button"
                      :aria-label="`Déplacer le thème '${theme.title}' vers le bas`"
                      title="Déplacer le thème vers le bas"
                      @click="moveThemeDown(themeIndex)">
                <span class="fa fa-chevron-down" aria-hidden="true"></span>
                <span class="sr-only">Vers le bas</span>
              </button>
              <div class="not-sr-only">
                {{ themeIndex + 1 }}
              </div>
            </div> 
          </td>
          <td class="flex-grow-1 flex-column justify-content-center">
            {{ theme.title }}
          </td>
        </tr>
      </transition-group>
    </table>
  </div>
</confirm-modal>
</template>

<script>
import '../../css/themes.css'
import axios from 'axios'
import backendUrls from '../utils/backend'
import ConfirmModal from '../utils/ConfirmModal'
import ErrorBar from '../utils/ErrorBar'
import { defineComponent } from 'vue'
// Suppression de: import { mapFields } from 'vuex-map-fields'
import { mapState, mapMutations } from 'vuex' // mapMutations peut être utile
// Suppression de: import SwapMixin from '../utils/SwapMixin'

export default defineComponent({
  components: {
    ConfirmModal,
    ErrorBar,
  },
  // mixins: [ SwapMixin ], // Remplacé par une logique interne ou un Composables

  data() {
    return {
      errorMessage: undefined,
    }
  },
  computed: {
    // Remplacement de mapFields('currentQuestionnaire.themes') par un getter/setter natif
    themes: {
      get() {
        return this.$store.state.currentQuestionnaire.themes || []
      },
      set(newThemes) {
        // Cette mutation doit être ajoutée à votre store.js
        this.$store.commit('setCurrentQuestionnaireThemes', newThemes)
      }
    },
  },
  methods: {
    // Hypothèse de la logique de Swap : Echanger les éléments et mettre à jour le store
    // (ceci remplace les appels au SwapMixin)
    swapItems(array, fromIndex, toIndex) {
      if (toIndex < 0 || toIndex >= array.length) return;
      
      const newArray = [...array]; // Copie pour éviter la mutation directe du state (strict mode)
      [newArray[fromIndex], newArray[toIndex]] = [newArray[toIndex], newArray[fromIndex]];
      
      // Mettre à jour l'ordre de chaque thème pour la persistance immédiate
      newArray[fromIndex].order = fromIndex + 1;
      newArray[toIndex].order = toIndex + 1;

      // Utiliser le setter de la computed property 'themes' pour mettre à jour le store
      this.themes = newArray;
      
      return newArray;
    },

    moveThemeUp(themeIndex) {
      if (themeIndex === 0) return;
      const newThemes = this.swapItems(this.themes, themeIndex, themeIndex - 1);
      
      // Suppression de la dépendance à jQuery pour la manipulation DOM:
      // const selectedJqueryElement = $('#move-themes-modal-theme-' + themeIndex)
      // this.swapMixin_moveItemUp(array, themeIndex, selectedJqueryElement)

      // Sauvegarde des deux thèmes affectés (celui qui monte et celui qui descend)
      if (newThemes) {
        this.saveThemeOrder(themeIndex - 1); // Le nouveau thème
        this.saveThemeOrder(themeIndex); // L'ancien thème
      }
    },

    moveThemeDown(themeIndex) {
      if (themeIndex === (this.themes.length - 1)) return;
      const newThemes = this.swapItems(this.themes, themeIndex, themeIndex + 1);
      
      // Suppression de la dépendance à jQuery
      // const selectedJqueryElement = $('#move-themes-modal-theme-' + themeIndex)
      // this.swapMixin_moveItemDown(array, themeIndex, selectedJqueryElement)

      // Sauvegarde des deux thèmes affectés
      if (newThemes) {
        this.saveThemeOrder(themeIndex); // L'ancien thème
        this.saveThemeOrder(themeIndex + 1); // Le nouveau thème
      }
    },

    clearError() {
      this.errorMessage = undefined
    },

    saveThemeOrder(themeIndex) {
      this.clearError()
      const theme = this.themes[themeIndex]
      if (!theme) return;

      return axios.put(
        backendUrls.theme(theme.id),
        {
          title: theme.title, 
          order: theme.order,
        })
        .catch(err => {
          this.errorMessage = 'Erreur lors de l\'enregistrement du thème : ' +
            (err.message ? err.message : JSON.stringify(err))
        })
    },
    
    // Si la modale a un événement 'confirm', il doit être géré ici.
    handleConfirm() {
      this.saveThemeOrder(); // Sauvegarde finale (si nécessaire)
      // Fermer la modale (doit être géré par le composant parent ou la modale elle-même)
    }
  }
})
</script>