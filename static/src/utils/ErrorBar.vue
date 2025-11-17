<template>
  <div class="alert alert-danger alert-icon alert-dismissible" role="alert">
    <button v-if="!noclose" type="button" class="close" data-dismiss="alert" @click="dismissed">
    <span class="sr-only">Fermer</span>
    </button>
    <span class="fe fe-alert-triangle" aria-hidden="true"></span>
    <slot></slot>
  </div>
</template>

<script>
export default {
  name: 'Dismissable',
  props: {
    noclose: Boolean,
  },
  emits: ['dismissed'],
  methods: {
    dismissed() {
      this.$emit('dismissed')
    },
  },
}
</script>

