<template>
  <div class="modal" tabindex="-1" role="dialog">
    <div class="modal-dialog large-modal" role="document">
      <div class="modal-content">
        <div class="modal-header border-bottom-0">
          <span class="fa fa-exchange-alt mr-2 mt-3" aria-hidden="true"></span>
          <div id="modal_title" class="modal-title">
            Transférer les droits de rédaction du questionnaire
          </div>
          <button type="button"
                  class="close"
                  data-dismiss="modal"
                  aria-label="Fermer">
            <span class="sr-only">Fermer</span>
          </button>
        </div>

        <div class="modal-body">

          <p class="mx-5">
            <strong>À qui souhaitez-vous transférer les droits de rédaction de ce questionnaire ?</strong>
          </p>

          <error-bar v-if="errorMessage" class="mx-5">
            <p>{{ errorMessage }}</p>
          </error-bar>

          <div class="card-body">

            <div class="card">
              <div class="card-body">
                <div class="flex-row align-items-center">
                  <div class="flex-column mr-4 flex-grow-1">
                    <strong>Libérer les droits de rédaction pour toute l'équipe</strong>
                    <p>Chacun.e de vos collègues pourra à son tour les prendre pour rédiger.</p>
                  </div>
                  <div class="flex-column mr-4">
                    <button
                      class="btn btn-primary"
                      title="Transférer"
                      @click="unsetEditor()">
                      <span class="fa fa-lock-open mr-2" aria-hidden="true"></span>
                      Libérer les droits
                    </button>
                  </div>
                </div>
              </div>
            </div>

            <div class="card">
              <div class="card-header justify-content-between">
                <h2 class="card-title">
                  <span class="fa fa-university mr-2" aria-hidden="true"></span>
                  <strong>Équipe d'instruction</strong>
                </h2>
              </div>

              <editor-list
                :users="inspectorUsers()"
                :questionnaireId="questionnaireId"
                @swap-editor="swapEditor">
              </editor-list>
            </div>

            <contact-support></contact-support>

          </div> <!-- end card-body -->

        </div> <!-- end modal-body -->
      </div> <!-- end modal-content -->
    </div> <!-- end modal-dialog -->
  </div> <!-- end modal -->
</template>

<script>
import '../../css/editors.css'
import { computed, onMounted, ref, defineComponent } from 'vue'
import { useStore } from 'vuex'
import axios from 'axios'
import backendUrls from '../utils/backend.js'
import ContactSupport from '../utils/ContactSupport'
import EditorList from './EditorList'
import ErrorBar from '../utils/ErrorBar'

export default defineComponent({
  props: {
    controlId: Number,
    questionnaireId: Number,
  },
  setup(props, { emit }) {
    const store = useStore()
    const users = ref([])
    const errorMessage = ref(undefined)

    // Remplace mapFields(['sessionUser'])
    const sessionUser = computed(() => store.state.sessionUser)

    const getUsers = () => {
      axios.get(backendUrls.getUsersInControl(props.controlId))
        .then((response) => {
          users.value = response.data
        })
    }

    const inspectorUsers = () => {
      return users.value.filter(item => 
        item.profile_type === 'inspector' && item.id !== sessionUser.value.id
      )
    }

    const swapEditor = (user) => {
      errorMessage.value = undefined
      emit('swap-editor', user)
    }

    const unsetEditor = () => {
      errorMessage.value = undefined
      emit('unset-editor')
    }

    const showError = (msg) => {
      errorMessage.value = msg
    }

    onMounted(() => {
      getUsers()
    })

    return {
      users,
      errorMessage,
      sessionUser,
      getUsers,
      inspectorUsers,
      swapEditor,
      unsetEditor,
      showError,
    }
  },
  components: {
    ContactSupport,
    EditorList,
    ErrorBar,
  },
})
</script>

