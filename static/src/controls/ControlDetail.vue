<template>
  <div class="page-main flex-row">
    <div id="sidebar-vm" class="border-right">
      <Sidebar />
    </div>
    <main class="mt-3 mt-md-5 flex-grow-1 ml-6 ie-flex-row-child" role="main">
      <span id="contenu" class="sr-only">Début du contenu principal</span>
      <ControlPage />
    </main>
  </div>
</template>

<script>
import ControlPage from './ControlPage'
import Sidebar from '../utils/Sidebar'

export default {
  name: 'ControlDetail',
  components: {
    ControlPage,
    Sidebar,
  },
  data() {
    return {
      noAccess: false,
    }
  },
}
</script>
