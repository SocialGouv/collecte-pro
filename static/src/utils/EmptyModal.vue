<template>
  <div class="modal" tabindex="-1" role="dialog" :data-keyboard="!noClose" :data-backdrop="noClose ? 'static' : true"  :aria-labelledby="titleId" aria-modal="true">
    <div class="modal-dialog" role="document">
      <div class="modal-content">
        <slot></slot>
      </div>
    </div>
  </div>

</template>

<script>
import { defineComponent } from 'vue'

export default defineComponent({
  name: 'EmptyModal',
  props: {
    noClose: Boolean,
    // Title/Id of the modal
    titleId: {
      type: String,
      default: 'modal_title',
    },
  },
})
</script>
