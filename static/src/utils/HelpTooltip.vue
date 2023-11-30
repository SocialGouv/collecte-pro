<template>
  <span data-html="true" data-toggle="tooltip" data-placement="right" :title="text" class="help-tooltip">
    <span :class="iconClass"></span>
  </span>
</template>

<script>
import '../../css/utils.css'
import Vue from 'vue'

export default Vue.extend({
  props: {
    text: String,
    iconClass: {
      type: String,
      default: 'fe fe-help-circle',
    },
  },
  mounted: function() {
    // Initialize tooltips
    $('[data-toggle="tooltip"]').tooltip()
  },
})

</script>
