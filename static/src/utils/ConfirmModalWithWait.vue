<template>
  <empty-modal :no-close="noClose">
    <form id="modalform" @submit.prevent>
      <div class="modal-header border-bottom-0">
        <div id="modal_title" class="modal-title">{{ title }}</div>
        <button v-if="!noClose"
                type="button"
                class="close"
                data-dismiss="modal"
                aria-label="Fermer"
                @click="closeModal">
                <span class="sr-only">Fermer</span>
        </button>
      </div>
      <div class="modal-body">
        <error-bar v-if="errorMessage">
          <p>{{ errorMessage }}</p>
        </error-bar>
        <slot></slot>
      </div>
      <div class="modal-footer border-top-0">
        <button v-if="confirmButton" type="submit" class="btn btn-primary"
                @click="confirmClicked"
                :class="{'btn-loading': processing}"
        >
          {{ confirmButton }}
        </button>
        <button v-if="cancelButton" type="button" class="btn btn-secondary"
                data-dismiss="modal"
                @click="cancelClicked"
        >
          {{ cancelButton }}
        </button>
      </div>
    </form>
  </empty-modal>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted } from 'vue'
import EmptyModal from './EmptyModal.vue'
import ErrorBar from './ErrorBar.vue'
import reportValidity from 'report-validity'

export default defineComponent({
  name: 'ConfirmModalWithWait',
  props: {
    cancelButton: String,
    confirmButton: String,
    noClose: Boolean,
    title: String,
  },
  emits: ['confirm', 'cancel', 'close'],
  setup(props, { emit }) {
    const errorMessage = ref('')
    const processing = ref(false)
    const modalEl = ref<HTMLElement | null>(null)

    const validateForm = () => {
      if (!modalEl.value) return true
      const forms = modalEl.value.getElementsByTagName('form')
      if (forms.length > 0) {
        return reportValidity(forms[0])
      }
      return true
    }

    const confirmClicked = () => {
      if (!modalEl.value) return

      errorMessage.value = ''
      if (!validateForm()) return

      const processingDoneCallback = (errMsg?: string, successMsg?: string, refreshUrl?: string) => {
        if (errMsg) {
          console.log('error!', errMsg)
          errorMessage.value = errMsg
          processing.value = false
          return
        }
        if (refreshUrl) {
          window.location.href = refreshUrl
        }
      }

      processing.value = true
      emit('confirm', processingDoneCallback)
    }

    const cancelClicked = () => {
      processing.value = false
      errorMessage.value = ''
      emit('cancel')
    }

    const closeModal = () => {
      processing.value = false
      errorMessage.value = ''
      emit('close')
    }

    onMounted(() => {
      modalEl.value = document.getElementById('modalform')
    })

    return {
      errorMessage,
      processing,
      confirmClicked,
      cancelClicked,
      closeModal,
      modalEl,
    }
  },
  components: {
    EmptyModal,
    ErrorBar,
  },
})
</script>
