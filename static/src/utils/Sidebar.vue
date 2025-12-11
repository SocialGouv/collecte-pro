<template>
 <nav class="sidebar" :class="{ collapsed: collapsed }" role="navigation">
  <button
    id="sidebar-toggle-button"
    class="btn btn-secondary"
    @click="toggleCollapse"
    :aria-expanded="!collapsed"
    aria-controls="sidebar"
    :aria-label="collapsed ? 'Ouvrir le panneau latéral' : 'Replier le panneau latéral'"
  >
    <span v-show="!collapsed" class="fa fa-chevron-left"></span>
    <span v-show="collapsed" class="fa fa-chevron-down"></span>
    <span v-show="collapsed">Ouvrir le menu</span>
    <span v-show="!collapsed" class="hidden">Replier le panneau latéral</span>
  </button>

  <div
    id="sidebar"
    ref="sidebar"
    v-show="!collapsed"
    :aria-hidden="collapsed ? 'true' : 'false'"
  >
    <sidebar-menu
      :menu="menu"
      :relative="true"
      :hideToggle="true"
      :show-one-child="true"
      theme="white-theme"
      @item-click="onItemClick"
    >
        <template #header>
          <div id="sidebar-title" class="card-header flex-row justify-content-center">
            <h2 class="card-title text-nowrap text-center">Mes espaces de dépôt</h2>
          </div>

          <div v-if="isLoaded && controls.length === 0">
            <div class="text-muted card-title text-center mx-7 mt-10 mb-4">
              <div v-if="user.is_inspector">
                Vous n'avez pas encore créé d'espace de dépôt.
              </div>
              <div v-else>
                Vous n'avez pas d'espace de dépôt.
              </div>
            </div>
          </div>

          <div v-if="user && user.is_inspector" class="card-header flex-row justify-content-center border-0">
            <control-create></control-create>
          </div>

          <div v-if="isLoaded && controls.length === 0" class="ie-margin-for-footer">
            <!-- empty div. Adds margin-bottom to fix a footer bug for IE. -->
          </div>

          <div v-if="!isLoaded && !hasError" class="sidebar-load-message card-header border-0 mt-4 mb-4">
            <div class="loader mr-2"></div>
            En attente de la liste d'espaces...
          </div>

          <error-bar id="sidebar-error-bar" v-if="hasError" :noclose="true">
            <div>
              <p>Nous n'avons pas pu obtenir vos espaces de dépôt.</p>
            </div>
            <div class="mt-2">
              <p>Erreur : {{ errorMessage }}</p>
            </div>
            <div class="mt-2">
              <p>Vous pouvez essayer de recharger la page
                <template v-if="!errorEmailLink">.</template>
                <template v-else>
                  , ou
                  <a
                    :href="'mailto:' + errorEmailLink + JSON.stringify(error)"
                    target="_blank"
                    rel="noopener noreferrer"
                  >
                    cliquez ici pour nous contacter
                  </a>.
                </template>
              </p>
            </div>
          </error-bar>
        </template>
      </sidebar-menu>
    </div>
  </nav>
</template>
<script>
import backend from '../utils/backend.js'
import ControlCreate from '../controls/ControlCreate'
import ErrorBar from '../utils/ErrorBar'
import { mapState } from 'vuex'
import { loadStatuses } from '../store'
import { SidebarMenu } from 'vue3-sidebar-menu'
import 'vue3-sidebar-menu/dist/vue-sidebar-menu.css'
import './sidebar-styles.css'
import axios from 'axios'
import { defineComponent } from 'vue'

const ERROR_EMAIL_BODY = 'Bonjour,%0D%0A%0D%0A' +
  'Je voudrais vous signaler une erreur lors du chargement des espaces de dépôt dans le menu.' +
  ' Les détails sont ci-dessous.%0D%0A%0D%0ACordialement,%0D%0A%0D%0A%0D%0A-----------%0D%0A'
const ERROR_EMAIL_SUBJECT = 'Erreur de chargement des espaces de dépôt'

export default defineComponent({
  name: 'Sidebar',
  components: {
    ControlCreate,
    ErrorBar,
    SidebarMenu,
  },
  props: {
    window: {
      default: () => window,
    },
    accessType: { type: String, default: '' },
  },
  data() {
    return {
      collapsed: false,
      hasError: false,
      error: undefined,
      errorMessage: undefined,
      isMenuBuilt: false,
      menu: [],
      showSidebar: true,
      currentAccessType: '',
    }
  },
  computed: {
    ...mapState({
      config: 'config',
      user: 'sessionUser',
      userLoadStatus: 'sessionUserLoadStatus',
      controls: 'controls',
      controlsLoadStatus: 'controlsLoadStatus',
    }),
    isLoaded() {
      return this.controlsLoadStatus === loadStatuses.SUCCESS &&
        this.userLoadStatus === loadStatuses.SUCCESS
    },
    errorEmailLink() {
      if (typeof this.config.support_team_email !== 'undefined') {
        return this.config.support_team_email + '?subject=' + ERROR_EMAIL_SUBJECT +
          '&body=' + ERROR_EMAIL_BODY
      }
      return undefined
    },
  },
  watch: {
    controlsLoadStatus(newValue) {
      if (this.showSidebar && newValue === loadStatuses.ERROR) {
        this.displayError('Erreur lors du chargement des espaces. Essayez de recharger la page.')
      }
    },
    userLoadStatus(newValue) {
      if (this.showSidebar && newValue === loadStatuses.ERROR) {
        this.displayError('Erreur lors du chargement des espaces. Essayez de recharger la page.')
      }
    },
    isLoaded(newValue) {
      if (this.showSidebar && newValue) {
        this.buildMenu()
      }
    },
  },
  mounted() {
    console.debug('this.window.location.pathname', this.window.location.pathname)
    if (this.window.location.pathname === backend.welcome()) {
      this.showSidebar = false
      return
    }
    if (this.isLoaded) {
      this.buildMenu()
    }
  },
  methods: {
    async onItemClick(event, item) {
      const targetElement = event.target
      if (targetElement.matches('span.vsm--badge.fas.fa-thumbtack')) {
        targetElement.classList.toggle('unpinned')
        const isPinned = !targetElement.classList.contains('unpinned')
        await this.markAsPinned(item.ctrl_id, isPinned)
      }
    },
    async markAsPinned(ctrl_id, isPinned) {
      try {
        const payload = { is_pinned: isPinned }
        const response = await axios.patch(backend.control(ctrl_id), payload)
        this.is_pinned = response.data.is_pinned
      } catch (error) {
        console.error(error)
        this.errors = error.response?.data
        this.hasErrors = true
      }
    },
    displayError(err) {
      this.hasError = true
      this.errorMessage = err.message ? err.message : err
      this.error = err
    },
    async buildMenu() {
      const currentURL = this.window.location.pathname
      const menu = []

      // Charger l'accessType pour chaque contrôle en séquence (rapide car pas de parallélisation)
      for (const control of this.controls) {
        await this.getAccessTypeLibelle(control.id)
        
        const titleLine1 = control.reference_code
        const titleLine2 = control.depositing_organization || control.title
        const title = titleLine1 + '\n' + titleLine2

        const controlMenu = {
          icon: this.currentAccessType === 'demandeur' && control.is_model ? 'far fa-file-alt' : 'fa fa-archive',
          href: backend['control-detail'](control.id),
          title: title,
          ctrl_id: control.id,
          is_model: control.is_model,
          attributes: { title: this.currentAccessType === 'demandeur' && control.is_model ? 'Espace de dépôt modèle' : '' },
        }

        if (control.is_model && this.currentAccessType === 'demandeur') {
          controlMenu.badge = {
            icon: 'fas fa-thumbtack',
            class: `fas fa-thumbtack ${control.is_pinned ? '' : 'unpinned'}`,
            attributes: { role: 'img', 'aria-label': 'épinglé', 'title': control.is_pinned ? 'épinglé' : 'épingler cet espace' },
          }
        }

        // Ajouter les questionnaires si on n'est pas sur les pages spéciales
        if (!['/faq/', '/declaration-conformite/', '/cgu/'].includes(currentURL)) {
          const children = control.questionnaires
            .filter(q => this.currentAccessType === 'demandeur' || !q.is_draft)
            .map(questionnaire => {
              const item = { href: backend['questionnaire-detail'](questionnaire.id), title: 'Questionnaire ' + questionnaire.numbering + ' - ' + questionnaire.title }
              if (backend.getIdFromViewUrl(currentURL, 'trash') === questionnaire.id) {
                item.child = [{ href: backend.trash(questionnaire.id), title: 'Corbeille' }]
              }
              return item
            })
          if (children.length) controlMenu.child = children

          const controlCreatingQuestionnaire = backend.getIdFromViewUrl(currentURL, 'questionnaire-create')
          if (controlCreatingQuestionnaire === control.id) {
            controlMenu.child = controlMenu.child || []
            controlMenu.child.push({ href: backend['questionnaire-create'](control.id), title: 'Q' + (controlMenu.child.length + 1) })
          }
        }

        menu.push(controlMenu)
      }

      // Trier après avoir ajouté tous les éléments
      menu.sort((a, b) => {
        // Les modèles (is_model) en haut
        if (a.is_model && !b.is_model) return -1
        if (!a.is_model && b.is_model) return 1
        // Ensuite les épinglés
        const aPinned = a.badge && !a.badge.class.includes('unpinned')
        const bPinned = b.badge && !b.badge.class.includes('unpinned')
        if (aPinned && !bPinned) return -1
        if (!aPinned && bPinned) return 1
        return b.ctrl_id - a.ctrl_id
      })

      this.isMenuBuilt = true
      this.menu = menu
    },
    toggleCollapse() {
      this.collapsed = !this.collapsed
      setTimeout(() => {
        if (this.$refs.sidebar) {
          this.$refs.sidebar.classList.toggle('hidden')
        }
      }, 300)
    },
    async getAccessTypeLibelle(ctlId) {
      const resp = await axios.get(backend.getAccessToControl(ctlId))
      const accessType = resp.data[0].access_type
      this.currentAccessType = accessType === 'demandeur' ? 'demandeur' : 'repondant'
      return this.currentAccessType
    },
  },
})
</script>
<style scoped>
</style>