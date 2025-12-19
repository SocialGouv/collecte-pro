<template>
  <span data-html="true" data-toggle="tooltip" data-placement="right" :title="text" class="help-tooltip">
    <span :class="iconClass"></span>
  </span>
</template>

<script>
import '../../css/utils.css'

export default {
  name: 'HelpTooltip',
  props: {
    text: String,
    iconClass: {
      type: String,
      default: 'fe fe-help-circle',
    },
  },
  mounted() {
    // Initialize tooltips
    $('[data-toggle="tooltip"]').tooltip()
  },
}
</script>

