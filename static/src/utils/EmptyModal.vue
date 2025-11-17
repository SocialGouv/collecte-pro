<template>
  <div class="modal" tabindex="-1" role="dialog" :data-keyboard="!noClose" :data-backdrop="noClose ? 'static' : true"  aria-labelledby="modal_title" aria-modal="true">
    <div class="modal-dialog" role="document">
      <div class="modal-content">
        <slot></slot>
      </div>
    </div>
  </div>

</template>

<script>
export default {
  name: 'YourComponentName',
  props: {
    noClose: Boolean,
  },
}
</script>
