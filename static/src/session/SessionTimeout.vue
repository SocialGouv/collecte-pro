<template>
  <div>
    <confirm-modal
      ref="idleModal"
      id="IdleSessionConfirmModal"
      title="Votre session va bientôt expirer..."
      confirm-button="Garder ma session active"
      @confirm="keepAlive"
      @close="keepAlive"
    >
      <p>Sans action de votre part, votre session va expirer.</p>
    </confirm-modal>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, computed, onMounted } from 'vue'
import axios from 'axios'
import ConfirmModal from '../utils/ConfirmModal.vue'

export default defineComponent({
  name: 'IdleSessionTimeout',
  components: { ConfirmModal },
  props: {
    logoutUrl: { type: String, required: true },
    expireSeconds: { type: Number, required: true },
  },
  setup(props) {
    const idleModal = ref<InstanceType<typeof ConfirmModal> | null>(null)
    const timeout = ref<number | null>(null)
    const gracePeriodMs = 30_000 // 30 sec

    const frontendExpireMs = computed(() => {
      return (props.expireSeconds * 0.9) * 1000
    })

    const showModal = () => {
      idleModal.value?.$el.classList.add('show') // simple alternative pour Vue 3
    }

    const keepServerAlive = () => {
      axios.get('/api/session/keep-alive').then(() => {
        console.debug('Keep server alive')
      })
    }

    const startSessionTimer = () => {
      console.debug('Start or restart session timer: ' + frontendExpireMs.value)
      if (timeout.value) clearTimeout(timeout.value)
      timeout.value = window.setTimeout(startGracePeriod, frontendExpireMs.value)
    }

    const startGracePeriod = () => {
      showModal()
      console.debug('Start grace period for idle session')
      timeout.value = window.setTimeout(() => {
        console.debug('End of grace period, logging out at ' + props.logoutUrl)
        window.location.href = props.logoutUrl
      }, gracePeriodMs)
    }

    const keepAlive = () => {
      if (timeout.value) clearTimeout(timeout.value)
      startSessionTimer()
      keepServerAlive()
    }

    onMounted(() => {
      console.debug('Mounted session timeout component')
      startSessionTimer()
    })

    return { idleModal, keepAlive }
  },
})
</script>
