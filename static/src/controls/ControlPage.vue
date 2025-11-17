<template>
  <div id="page-content" class="mx-3">

    <div id="controls">
      <div v-if="controls.length === 0">
        <no-controls v-if="user.is_inspector">
        </no-controls>
        <div v-else class="card">
          <div class="card-body">
            <p>Vous n'avez accès à aucun espace de dépôt. Si vous avez besoin d'un accès, contactez l'équipe d'instruction.</p>
          </div>
        </div>
      </div>

      <template v-else>
        <control-card v-if="displayedControl !== undefined"
                      :key="displayedControl.id"
                      :control="displayedControl"
                      :user="user"
                      :accessType="accessType"
        >
        </control-card>
      </template>
    </div>

    <add-user-modal></add-user-modal>

    <update-user-modal></update-user-modal>

    <remove-user-modal></remove-user-modal>

  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue'
import { mapState } from 'vuex'
import axios from 'axios'
import backendUrls from '../utils/backend'

import AddUserModal from '../users/AddUserModal.vue'
import ControlCard from './ControlCard.vue'
import NoControls from './NoControls.vue'
import RemoveUserModal from '../users/RemoveUserModal.vue'
import UpdateUserModal from '../users/UpdateUserModal.vue'

export default defineComponent({
  name: 'ControlPage',
  components: {
    AddUserModal,
    ControlCard,
    NoControls,
    RemoveUserModal,
    UpdateUserModal,
  },
  data() {
    return {
      hash: '',
      accessType: '',
    }
  },
  computed: {
    ...mapState({
      user: 'sessionUser',
      controls: 'controls',
    }),
    displayedControl() {
      return this.controls.find(control => this.hash === '#control-' + control.id)
    },
  },
  mounted() {
    const isValidHash = (hash: string) => /^#control-[0-9]+$/.test(hash)

    const hashPointsToExistingControl = (hash: string) => {
      if (!isValidHash(hash)) return false
      const controlId = parseInt(hash.replace('#control-', ''), 10)
      if (isNaN(controlId)) return false
      if (this.controls.map(c => c.id).includes(controlId)) return true
      // Contrôle non accessible
      if (this.$parent) (this.$parent as any).noAccess = true
      return false
    }

    const updateHash = () => {
      console.debug('hashchange', window.location.hash)
      if (!hashPointsToExistingControl(window.location.hash) && this.controls.length > 0) {
        window.location.hash = '#control-' + this.controls[0].id
        return
      }
      this.hash = window.location.hash
    }

    window.addEventListener('hashchange', updateHash, false)
    updateHash()

    if (this.displayedControl) {
      this.getAccessType(this.displayedControl.id)
    }
  },
  watch: {
    displayedControl: {
      handler(newVal) {
        if (newVal) this.getAccessType(newVal.id)
      },
      deep: true,
      immediate: true,
    },
  },
  methods: {
    async getAccessType(displayedControlId: number) {
      try {
        const resp = await axios.get(backendUrls.getAccessToControl(displayedControlId))
        this.accessType =
          resp.data?.[0]?.access_type ?? ''
      } catch (error) {
        console.error("Erreur sur l'access type : ", error)
      }
    },
  },
})
</script>
