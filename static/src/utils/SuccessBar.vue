<template>
  <div class="alert alert-success alert-icon alert-dismissible" role="status">
    <button v-if="!noclose" type="button" class="close" data-dismiss="alert" @click="dismissed">.
    <span class="sr-only">Fermer</span>
    </button>
    <em class="fe fe-check" aria-hidden="true"></em>
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
