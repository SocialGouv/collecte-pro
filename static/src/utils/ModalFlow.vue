<!--
  A flow in three modals (that you specify in three corresponding slots):
   - 1 - confirm-modal: The user clicks checkboxes (or fills whatever other form) to validate that
   they really want to take the action.<style scoped>
   - 2 - waiting-modal: the action is taken in the background (e.g. API call) while a wait message
   is displayed.
   - 3 - success-modal: the action has successfully been taken, a success modal is displayed.

  The action to take is specified by passing actionFunction as a prop. The function should return a
  Promise, that either resolves, or rejects with an error whose message will be displayed to
  the user.

  To trigger the start of the flow, you need to call ModalFlow's "start" method.

  See ControlDeleteFlow.vue for an example of use.

  Optional : if you want to customize how errors are displayed, you can use the slot named
  "error-message". To use the error object, you need to fetch it in the ModalFlow object. See
  PublishFlow.vue for an example.

-->
<template>
  <div>
    <empty-modal ref="confirmModal" class="confirm-modal" :no-close="true">
      <error-bar v-if="error !== undefined" class="m-3">
        <!-- The "error-message" slot should be displayed if specified, otherwise display a default
        layout. -->
        <div v-if="hasCustomError">
          <slot name="error-message"></slot>
        </div>
        <div v-else-if="error.message !== undefined">
          {{ error.message }}
        </div>
        <div v-else>
          {{ error }}
        </div>
      </error-bar>
      <form @submit.prevent="confirmed">
        <!--
          This slot should contain the form, which when submitted will trigger the rest of the
          flow.
          Typically a title, one or more required checkboxes, a cancel button and a submit button.
        -->
        <slot name="confirm-modal-form"></slot>
      </form>
    </empty-modal>

    <empty-modal ref="waitingModal"
                 no-close="true">
      <div class="d-flex flex-column align-items-center p-8">
        <div class="m-4">
          <!--
            This slot should contain the wait message, something like "Action is happening..."
          -->
          <slot name="wait-message"></slot>
        </div>
        <div class="loader m-4"></div>
      </div>
    </empty-modal>

    <empty-modal ref="successModal"
                 no-close="true">
      <!--
        This slot should contain the success modal.
      -->
      <slot name="success-modal-body"></slot>
    </empty-modal>

  </div>
</template>

<script>
import { ref, computed, defineComponent } from 'vue'
import EmptyModal from './EmptyModal'
import ErrorBar from './ErrorBar'

const SPINNER_DURATION_MILLIS = 2000

export default defineComponent({
  name: 'ConfirmModalWithWait',
  components: {
    EmptyModal,
    ErrorBar,
  },
  props: {
    // The function to run once the user has confirmed they really want to take the action.
    actionFunction: {
      type: Function,
      required: true,
    },
  },
  setup(props) {
    const error = ref(undefined)
    const confirmModal = ref(null)
    const waitingModal = ref(null)
    const successModal = ref(null)

    const hasCustomError = computed(() => {
      // In Vue 3, use slots directly instead of $scopedSlots
      return !!props.$slots?.['error-message']
    })

    function start() {
      console.debug('start!')
      $(confirmModal.value.$el).on('hidden.bs.modal', () => {
        error.value = undefined
      })
      $(confirmModal.value.$el).modal('show')
    }

    function wait(timeMillis) {
      return new Promise(resolve => {
        const id = setTimeout(() => {
          clearTimeout(id)
          resolve()
        }, timeMillis)
      })
    }

    async function confirmed() {
      console.debug('confirmed!')
      $(confirmModal.value.$el).modal('hide')
      $(waitingModal.value.$el).modal('show')
      error.value = undefined

      try {
        await Promise.all([wait(SPINNER_DURATION_MILLIS), props.actionFunction()])
        console.debug('Done action.')
        $(waitingModal.value.$el).modal('hide')
        $(successModal.value.$el).modal('show')
      } catch (err) {
        console.error('Error while doing the action:', err)
        error.value = err
        $(waitingModal.value.$el).modal('hide')
        $(confirmModal.value.$el).modal('show')
      }
    }

    return {
      error,
      confirmModal,
      waitingModal,
      successModal,
      hasCustomError,
      start,
      confirmed,
    }
  },
})
</script>
