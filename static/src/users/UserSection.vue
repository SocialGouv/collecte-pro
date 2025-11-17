<template>
  <div class="card">
    <div class="card-status card-status-top bg-blue"></div>
    <div class="card-header">
      <h2 class="card-title">
        <span class="fe fe-users mr-2" aria-hidden="true"></span>
        <span>Qui a accès à cet espace ?</span>
      </h2>
    </div>

    <div class="card-body">
      <div class="card">
        <div class="card-header justify-content-between">
          <h2 class="card-title">
            <span class="fa fa-university mr-2" aria-hidden="true"></span>
            <strong>Équipe d'instruction</strong>
          </h2>
          <button v-if="accessType === 'demandeur'"
                  data-toggle="modal"
                  data-target="#addUserModal"
                  @click="updateEditingState('inspector')"
                  class="btn btn-primary">
            <span class="fe fe-plus" aria-hidden="true"></span>
            Ajouter un demandeur
          </button>
        </div>
        <user-list :users="inspectorUsers" profile-type="inspector"
          :control="control" :accessType="accessType">
        </user-list>
      </div>

      <div class="card mb-0">
        <div class="card-header justify-content-between">
          <h2 class="card-title">
            <span class="fa fa-building mr-2" aria-hidden="true"></span>
            <strong>Organisme interrogé</strong>
          </h2>
          <button v-if="accessType === 'demandeur'"
                  data-toggle="modal"
                  data-target="#addUserModal"
                  @click="updateEditingState('audited')"
                  class="btn btn-primary">
            <span class="fe fe-plus" aria-hidden="true"></span>
            Ajouter un répondant
          </button>
        </div>
        <user-list :users="auditedUsers" profile-type="audited"
          :control="control" :accessType="accessType">
        </user-list>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, computed, onMounted } from 'vue'
import { useStore } from 'vuex'
import axios from 'axios'
import backendUrls from '../utils/backend'
import EventBus from '../events'
import UserList from './UserList.vue'

export default defineComponent({
  name: 'ControlUsers',
  components: { UserList },
  props: {
    control: { type: Object, default: () => ({}) },
    accessType: { type: String, default: '' },
  },
  setup(props) {
    const store = useStore()
    const auditedUsers = ref<any[]>([])
    const inspectorUsers = ref<any[]>([])

    // Computed avec getters et setters pour le store
    const editingControl = computed({
      get: () => store.state.editingControl,
      set: (value) => store.commit('setEditingControl', value),
    })

    const editingProfileType = computed({
      get: () => store.state.editingProfileType,
      set: (value) => store.commit('setEditingProfileType', value),
    })

    const sessionUser = computed(() => store.state.sessionUser)

    // Méthodes
    const getAuditedUsers = async () => {
      const response = await axios.get(backendUrls.getAuditedUsersInControl(props.control.id))
      auditedUsers.value = response.data
    }

    const getInspectorUsers = async () => {
      const response = await axios.get(backendUrls.getInspectorUsersInControl(props.control.id))
      inspectorUsers.value = response.data
    }

    const updateEditingState = (profileType: string) => {
      editingControl.value = props.control
      editingProfileType.value = profileType
    }

    // Lifecycle
    onMounted(() => {
      getAuditedUsers()
      getInspectorUsers()
      EventBus.$on('users-changed', () => {
        getAuditedUsers()
        getInspectorUsers()
      })
    })

    return {
      auditedUsers,
      inspectorUsers,
      editingControl,
      editingProfileType,
      sessionUser,
      getAuditedUsers,
      getInspectorUsers,
      updateEditingState,
    }
  },
})
</script>
