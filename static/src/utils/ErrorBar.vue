<template>
  <div class="alert alert-danger alert-icon alert-dismissible" role="alert">
    <button v-if="!noclose" type="button" class="close" data-dismiss="alert" @click="dismissed">
    <span class="sr-only">Fermer</span>
    </button>
    <i class="fe fe-alert-triangle" aria-hidden="true"></i>
    <slot></slot>
  </div>
</template>

<script>
import Vue from 'vue'

export default Vue.extend({
  props: ['noclose'],
  methods: {
    dismissed: function () {
      this.$emit('dismissed')
    },
  },
})

</script>
