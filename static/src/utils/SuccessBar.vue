<template>
  <div class="alert alert-success alert-icon alert-dismissible" role="status">
    <button v-if="!noclose" type="button" class="close" data-dismiss="alert" @click="dismissed">.
    <span class="sr-only">Fermer</span>
    </button>
    <span class="fe fe-check" aria-hidden="true"></span>
    <slot></slot>
  </div>
</template>

<script>
import { defineComponent } from 'vue'

export default defineComponent({
  name: 'InfoBar', // ou le nom de ton composant
  props: {
    noclose: Boolean,
  },
  methods: {
    dismissed() {
      this.$emit('dismissed')
    },
  },
})
</script>
