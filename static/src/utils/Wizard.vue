<template>
  <ul class="flex-row justify-content-around mb-6">
    <wizard-step v-for="(stepTitle, i) in stepTitles"
                 :key="'step-' + (i + 1)"
                 :number="i+1"
                 :class="{ 'active': activeI === i , 'done': activeI > i }"
                 :clickable="i === (activeI + 1) || i < activeI"
                 @clickedStep="clicked(i+1)"
    >
      {{ stepTitle }}
      <span v-if="activeI === i" class="sr-only">En cours de consultation</span>
      <span v-if="activeI > i" class="sr-only">Étape validée</span>
    </wizard-step>
  </ul>
</template>

<script>
import WizardStep from './WizardStep.vue'

export default {
  name: 'Wizard',
  props: {
    activeStepNumber: Number,
    stepTitles: Array
  },
  components: {
    WizardStep,
  },
  computed: {
    activeI() {
      return this.activeStepNumber - 1
    },
  },
  methods: {
    clicked(clickedStepNumber) {
      if (clickedStepNumber === (this.activeStepNumber + 1)) {
        this.$emit('next', clickedStepNumber)
        return
      }
      if (clickedStepNumber < this.activeStepNumber) {
        this.$emit('previous', clickedStepNumber)
        return
      }
    },
  },
}
</script>
