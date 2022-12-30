<template>
  <empty-modal :no-close="noClose">
    <div class="modal-header border-bottom-0">
      <div id="modal_title" class="modal-title">
        <span :class="iconClass + ' mr-2'"></span>
        {{ title }}
      </div>
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
      <slot></slot>
    </div>
    <div class="modal-footer border-top-0">
      <button v-if="confirmButton" type="button" class="btn btn-primary"
              data-dismiss="modal"
              @click="confirmClicked"
      >
        {{ confirmButton }}
      </button>
      <button v-if="confirmButtonPrevent" type="button" class="btn btn-primary"
        @click="confirmClicked"
      >
        {{ confirmButtonPrevent }}
      </button>
      <button v-if="cancelButton" type="button" class="btn btn-secondary"
              data-dismiss="modal"
              @click="cancelClicked"
      >
        {{ cancelButton }}
      </button>
    </div>
  </empty-modal>
</template>

<script>
import EmptyModal from './EmptyModal'
import Vue from 'vue'

export default Vue.extend({
  props: [
    'cancel-button',
    'confirm-button',
    'confirm-button-prevent',
    'icon-class',
    'no-close',
    'title',
  ],
  components: {
    EmptyModal,
  },
  methods: {
    confirmClicked () {
      this.$emit('confirm')
    },
    cancelClicked () {
      this.$emit('cancel')
    },
    closeModal () {
      this.$emit('close')
    },
  },
})

</script>

<style></style>
