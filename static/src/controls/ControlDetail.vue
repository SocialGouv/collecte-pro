<template>
  <div class="page-main flex-row">
    <div id="sidebar-vm" class="border-right">
      <sidebar></sidebar>
    </div>
    <main class="mt-3 mt-md-5 flex-grow-1 ml-6 ie-flex-row-child" role="main">
      <a name="contenu"> </a>
      <control-page>
      </control-page>
    </main>
  </div>
</template>

<script>
import ControlPage from './ControlPage'
import Sidebar from '../utils/Sidebar'
import Vue from 'vue'

export default Vue.extend({
  name: 'ControlDetail',
  data: function() {
    return {
      noAccess: false,
    }
  },
  components: {
    ControlPage,
    Sidebar,
  },
})
</script>
