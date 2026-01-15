<template>
  <empty-modal :no-close="true">
    <form @submit.prevent="confirm" class="modal-body">

      <div class="modal-header border-bottom-0">
        <div id="modal_title" class="modal-title">
          Vous êtes sur le point de forcer le transfert des droits
          de ce questionnaire, en conséquence :
        </div>
      </div>

      <label for="become-editor-checkbox-1" class="flex-row align-items-center mt-2" id="checkbox-1-label">
        <input class="mt-0"
               type="checkbox"
               id="become-editor-checkbox-1"
               required
               aria-labelledby="checkbox-1-label">
        <span class="ml-2">
          Les modifications non enregistrées de votre collègue seront perdues.
        </span>
      </label>

      <label for="become-editor-checkbox-2" class="flex-row align-items-center mt-2" id="checkbox-2-label">
        <input class="mt-0"
               type="checkbox"
               id="become-editor-checkbox-2"
               required
               aria-labelledby="checkbox-2-label">
        <span class="ml-2">
          Pour que d'autres puissent modifier ce questionnaire,
          vous devrez libérer ou transférer les droits de rédaction.
        </span>
      </label>

      <div class="modal-footer border-top-0">
        <button type="button"
                class="btn btn-secondary"
                data-dismiss="modal"
                title="Annuler">
          Annuler
        </button>
        <button type="submit"
                class="btn btn-primary"
                title="Forcer le transfert">
          <span class="fa fa-exchange-alt mr-1" aria-hidden="true"></span>
          Forcer le transfert
        </button>
      </div>

    </form>
  </empty-modal>
</template>

<script>
import { computed } from 'vue'
import { useStore } from 'vuex'
import EmptyModal from '../utils/EmptyModal'

export default {
  components: { EmptyModal },
  props: {},
  setup(props, { emit }) {
    const store = useStore()

    // Remplace mapFields('sessionUser')
    const sessionUser = computed(() => store.state.sessionUser)

    const confirm = () => {
      emit('confirm')
    }

    return {
      sessionUser,
      confirm,
    }
  },
}
</script>
