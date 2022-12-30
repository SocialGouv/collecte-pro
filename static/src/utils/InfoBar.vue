<template>
  <div class="alert alert-info alert-icon alert-dismissible" role="status">
    <button v-if="!noclose" type="button" class="close" data-dismiss="alert" @click="dismissed">
    <span class="sr-only">Fermer</span>
    </button>
    <span class="fe fe-info" aria-hidden="true"></span>
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
