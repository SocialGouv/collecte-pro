<template>
  <div v-bind:id="'theme' + themeNumbering"
       class="card">
    <div class="card-status card-status-top bg-blue"></div>
    <div class="card-header">
      <h2 class="card-title">{{ themeNumbering }}. {{ theme.title }}</h2>
    </div>

    <slot></slot>

  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue'

export default defineComponent({
  name: 'ThemeComponent',
  props: {
    theme: null,
    themeNumbering: null,
  },
})
</script>
