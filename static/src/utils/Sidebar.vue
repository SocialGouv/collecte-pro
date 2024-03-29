<template>
  <nav class="sidebar" :class="{ collapsed: collapsed }">
    <div v-if="showSidebar">
      <button id="sidebar-toggle-button" class="btn btn-secondary" @click="toggleCollapse" title="Replier le panneau latéral">
        <span v-show="!collapsed" class="fa fa-chevron-left"></span>
        <span v-show="collapsed" class="fa fa-chevron-down"></span>
        <span v-show="collapsed">Ouvrir le menu</span>
        <span v-show="!collapsed" class="hidden">Replier le panneau latéral</span>
      </button>
      <sidebar-menu class="sidebar-body"
                    id="sidebar"
                    :menu="menu"
                    :relative="true"
                    :hideToggle="true"
                    :show-one-child="true"
                    theme="white-theme"
                    :collapsed="collapsed"
                    v-if="!collapsed"
                    role="navigation"
      >
        <template v-slot:header>
          <div id="sidebar-title"
               class="card-header flex-row justify-content-center">
            <h1 class="card-title text-nowrap text-center">
              Mes espaces de dépôt
            </h1>
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

          <div v-if="user && user.is_inspector"
              class="card-header flex-row justify-content-center border-0">
            <control-create></control-create>
          </div>

          <div v-if="isLoaded && controls.length === 0"
              class="ie-margin-for-footer">
            <!-- empty div. Adds margin-bottom to fix a footer bug for IE. -->
          </div>

          <div v-if="!isLoaded && !hasError"
              class="sidebar-load-message card-header border-0 mt-4 mb-4">
            <div class="loader mr-2"></div>
            En attente de la liste d'espaces...
          </div>

          <error-bar id="sidebar-error-bar" v-if="hasError" noclose=true>
            <div>
              <p>Nous n'avons pas pu obtenir vos espaces de dépôt.</p>
            </div>
            <div class="mt-2">
              <p>Erreur : {{ errorMessage }}</p>
            </div>
            <div class="mt-2">
              <p>Vous pouvez essayer de recharger la page
              <template v-if="!errorEmailLink">
                .
              </template>
              <template v-else>
                , ou
                <a :href="'mailto:' + errorEmailLink + JSON.stringify(error)"
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  cliquez ici pour nous contacter
                </a>.</p>
              </template>
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
import { SidebarMenu } from 'vue-sidebar-menu'
import Vue from 'vue'
import 'vue-sidebar-menu/dist/vue-sidebar-menu.css'

import axios from 'axios'

const ERROR_EMAIL_BODY = 'Bonjour,%0D%0A%0D%0A' +
    'Je voudrais vous signaler une erreur lors du chargement des espaces de dépôt dans le menu.' +
    ' Les détails sont ci-dessous.%0D%0A%0D%0ACordialement,%0D%0A%0D%0A%0D%0A-----------%0D%0A'
const ERROR_EMAIL_SUBJECT = 'Erreur de chargement des espaces de dépôt'

export default Vue.extend({
  components: {
    ControlCreate,
    ErrorBar,
    SidebarMenu,
  },
  props: {
    // Pass window object as prop, so that we can pass a mock for testing.
    // Do not use "window" or "document" directly in this file, instead use "this.window" and
    // "this.window.document"
    window: {
      default: () => window,
    },
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
    controlsLoadStatus(newValue, oldValue) {
      if (this.showSidebar && newValue === loadStatuses.ERROR) {
        this.displayError('Erreur lors du chargement des espaces. Essayez de recharger la page.')
        return
      }
    },
    userLoadStatus(newValue, oldValue) {
      if (this.showSidebar && newValue === loadStatuses.ERROR) {
        this.displayError('Erreur lors du chargement des espaces. Essayez de recharger la page.')
        return
      }
    },
    isLoaded(newValue, oldValue) {
      if (this.showSidebar) {
        if (newValue === false) {
          return
        }
        this.buildMenu()
      }
    },
  },
  mounted: function() {
    console.debug('this.window.location.pathname', this.window.location.pathname)
    if (this.window.location.pathname === backend.welcome()) {
      this.showSidebar = false
      return
    }
    // If the data is already there (because it was prefetched from server), build menu now.
    // Else the watcher on isLoaded will trigger buildMenu when the data is loaded.
    if (this.isLoaded) {
      this.buildMenu()
    }
  },
  methods: {
    displayError(err) {
      this.hasError = true
      this.errorMessage = err.message ? err.message : err
      this.error = err
    },
    buildMenu() {
      console.debug('build menu')
      const makeControlTitle = control => {
        let title = control.reference_code + '\n'
        if (control.depositing_organization) {
          title += control.depositing_organization
        } else {
          title += control.title
        }
        return title
      }

      const makeQuestionnaireLink = questionnaire => {
        if (!questionnaire.is_draft) {
          return backend['questionnaire-detail'](questionnaire.id)
        }
        if (questionnaire.editor && questionnaire.editor.id === this.user.id) {
          return backend['questionnaire-edit'](questionnaire.id)
        }
        return backend['questionnaire-detail'](questionnaire.id)
      }

      // If we are on a create-questionnaire page, find the control for which the questionnaire is
      // being created.
      const controlCreatingQuestionnaire =
          backend.getIdFromViewUrl(this.window.location.pathname, 'questionnaire-create')

      // If we are on a trash page, find the control for which the trash folder is.
      const questionnaireForTrash = backend.getIdFromViewUrl(this.window.location.pathname, 'trash')

      const menu = []
      this.controls.forEach(async control => {
        const controlMenu = {
          icon: 'fa fa-archive',
          href: backend['control-detail'](control.id),
          title: makeControlTitle(control),
          ctrl_id: control.id,
        }

      const currentURL = this.window.location.pathname
      if (currentURL !== '/faq/' && currentURL !== '/declaration-conformite/' && currentURL !== '/cgu/' && currentURL.replace(/\d+\/$/, '') !== '/questionnaire/corbeille/') {

        const resp = await axios.get(backend.getAccessToControl(control.id))
        const accessType = resp.data[0].access_type
        const children = control.questionnaires.map(questionnaire => {
          if (accessType === 'demandeur' || !questionnaire.is_draft) {
            const questionnaireItem = {
              href: makeQuestionnaireLink(questionnaire),
              title: 'Questionnaire ' + questionnaire.numbering + ' - ' + questionnaire.title,
            }
            if (questionnaireForTrash === questionnaire.id) {
              questionnaireItem.child = [{
                href: backend.trash(questionnaire.id),
                title: 'Corbeille',
              }]
            }
            return questionnaireItem
          }
        }).filter(item => !!item)
        if (children.length > 0) {
          controlMenu.child = children
        }

        // Add menu item for the questionnaire being created, if there is one.
        if (controlCreatingQuestionnaire === (control.id)) {
          if (!controlMenu.child) {
            controlMenu.child = []
          }
          controlMenu.child.push({
            href: backend['questionnaire-create'](control.id),
            title: 'Q' + (controlMenu.child.length + 1),
          })
        }
      }
        menu.push(controlMenu)
        menu.sort((a, b) => { return b.ctrl_id - a.ctrl_id })
      })
      this.isMenuBuilt = true
      this.menu = menu
    },
    toggleCollapse() {
      this.collapsed = !this.collapsed;
      window.setTimeout(function() {
        $("#sidebar").toggleClass("hidden");
      },
      300);
    },
  },
})
</script>

<style scoped>
</style>

<style>
  #sidebar-vm {
    background-color: white;
  }

  /* Fix z-index for modal in CreateControl to be displayed correctly */
  .sidebar .v-sidebar-menu {
    z-index: unset;
  }

  /*
  Sidebar should not be too narrow, fix a min-width.
  The sidebar itself has a changing width (since it collapses, with an animation), so constrain the
  width of the sidebar-title instead.
  */
  #sidebar-title .card-title {
    min-width: 350px;
  }

  /* Place toggle button outside of the sidebar, in the navbar. */
  .sidebar {
    position: relative;
  }
  #sidebar-toggle-button {
    position: fixed;
    left: 350px;
    z-index: 1000; /* Just above sidebar items at z-index 999, but under modals at 1050 */
    transition: left 0.3s;
  }
  .collapsed #sidebar-toggle-button {
    transform: rotate(-90deg);
    left: -35px;
  }

  /* Don't show elements sticking out of the sidebar */
  .sidebar-body {
    overflow: hidden;
    /* Fix for IE : use inherit instead of unset, because IE doesn't know unset. This was breaking
    the modals placed inside the sidebar. */
    z-index: inherit;
  }

  /* Add borders to items */
  .v-sidebar-menu .vsm--item {
      border-bottom-width: 1px;
      border-bottom-style: solid;
      border-bottom-color: rgba(0, 40, 100, 0.12); /* same color as tabler borders */
  }
  .v-sidebar-menu .vsm--item:first-child {
      border-top-width: 1px;
      border-top-style: solid;
      border-top-color: rgba(0, 40, 100, 0.12); /* same color as tabler borders */
  }

  /* Wrap text for titles that overflow */
  .v-sidebar-menu .vsm--title {
    white-space: pre-wrap;
    /* Text was flowing over arrows */
    margin-right: 20px;
    word-break: break-word;
  }

  /* Style icons */
  .v-sidebar-menu.vsm_white-theme .vsm--icon,
  .v-sidebar-menu.vsm_white-theme .vsm--link_level-1 .vsm--icon {
    color: #495057;
    background-color: white;
  }
  .v-sidebar-menu.vsm_white-theme .vsm--link_level-1.vsm--link_exact-active .vsm--icon,
  .v-sidebar-menu.vsm_white-theme .vsm--link_level-1.vsm--link_active .vsm--icon {
    color: #495057;
    background-color: white;
  }

  /* Fix height of items when collapsed */
  .vsm_collapsed .vsm--item {
    height: 80px;
  }

  .v-sidebar-menu.vsm_white-theme.vsm_expanded .vsm--item_open .vsm--link_level-1 {
    background-color: #3473cb;
    color: #fff;
  }
  .v-sidebar-menu.vsm_white-theme.vsm_expanded .vsm--item_open .vsm--link_level-1 .vsm--icon {
    background-color: #3473cb;
  }
</style>
