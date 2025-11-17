<template>
  <div class="card-status card-status-left" :class="colorClass">
  </div>
</template>

<script>
const colorClasses = [
  'bg-blue',
  'bg-red',
  'bg-yellow',
  'bg-purple',
  'bg-green',
  'bg-teal',
]

export default {
  name: 'ColorBadge',
  props: {
    id: {
      type: Number,
      required: true,
    },
  },
  computed: {
    colorClass() {
      return colorClasses[this.id % colorClasses.length]
    },
  },
}
</script>

