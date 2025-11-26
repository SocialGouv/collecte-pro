<template>
  <h1 class="flex-row mb-5 text-muted breadcrumbs">
    <div class="mx-2">
      <span class="fa fa-archive" aria-hidden="true"></span>
      <span class="sr-only">Corbeille</span>
    </div>
    <div class="mx-2">
      <span class="fa fa-chevron-right" aria-hidden="true"></span>
      <span class="sr-only">&gt;</span>
    </div>
    <div class="mx-2">
      <a :href="controlLink">
        {{ control.reference_code }} -
        {{ control.depositing_organization !== undefined ?
              control.depositing_organization : control.title}}
      </a>
    </div>
  </h1>
</template>

<script>
import backendUrls from './backend'

import { defineComponent } from 'vue'

export default defineComponent({
  name: 'ControlBreadcrumb',
  props: {
    control: {
      type: Object,
      required: true,
    },
  },
  computed: {
    controlLink() {
      return backendUrls['control-detail'](this.control.id)
    },
  },
})
</script>

