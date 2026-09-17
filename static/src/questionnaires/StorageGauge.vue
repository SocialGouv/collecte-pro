<template>
  <div class="card storage-gauge">
    <div class="card-body">
      <div class="form-label">
        Espace utilisé pour le dépôt de fichiers : {{ label }}
      </div>
      <div class="progress">
        <div class="progress-bar"
             :class="colorClass"
             role="progressbar"
             :style="{ width: percent + '%' }"
             :aria-valuenow="percent"
             aria-valuemin="0"
             aria-valuemax="100">
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, computed } from 'vue'

const GO_IN_BYTES = 1024 * 1024 * 1024
const QUOTA_BYTES = GO_IN_BYTES

const formatSize = (bytes: number): string => {
  if (bytes >= GO_IN_BYTES) {
    return `${(bytes / GO_IN_BYTES).toFixed(2)} Go`
  }
  return `${(bytes / (1024 * 1024)).toFixed(0)} Mo`
}

export default defineComponent({
  name: 'StorageGauge',
  props: {
    usedBytes: { type: Number, required: true },
  },
  setup(props) {
    const percent = computed(() => Math.min(100, Math.round((props.usedBytes / QUOTA_BYTES) * 100)))
    const ratio = computed(() => props.usedBytes / QUOTA_BYTES)
    const colorClass = computed(() => {
      if (ratio.value >= 1) return 'bg-red'
      if (ratio.value >= 0.9) return 'bg-orange'
      if (ratio.value >= 0.75) return 'bg-green-light'
      return 'bg-green'
    })
    const label = computed(() => `${formatSize(props.usedBytes)} / 1 Go`)

    return {
      percent,
      colorClass,
      label,
    }
  },
})
</script>
