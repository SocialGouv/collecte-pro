<template>
  <li class="wizard-step">

    <a v-if="clickable"
       class="wizard-step-graphics"
       href="javascript:void(0);"
       @click.prevent="$emit('clickedStep')">
      <div class="wizard-step-thread"></div>
      <div class="wizard-step-bubble card-title">
        <span class="number">{{ number }}</span>
        <span class="done-icon fe fe-check" aria-hidden="true"></span>
      </div>
    </a>

    <div v-else
         class="wizard-step-graphics">
      <div class="wizard-step-thread"></div>
      <div class="wizard-step-bubble card-title">
        <span class="number">{{ number }}</span>
        <span class="done-icon fe fe-check" aria-hidden="true"></span>
      </div>
    </div>

    <slot></slot>
  </li>
</template>

<script>
import '../../css/utils.css'
import Vue from 'vue'

export default Vue.extend({
  props: ['number', 'clickable'],
})
</script>
