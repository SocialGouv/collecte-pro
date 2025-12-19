<template>
    <div class="modal" tabindex="-1" role="dialog">
      <div class="modal-dialog modal-video" role="document">
        <div class="modal-content">
          <div class="modal-header border-bottom-0">
            <button type="button"
                    class="close"
                    data-dismiss="modal"
                    aria-label="Fermer">
                    <span class="sr-only">Fermer</span>
            </button>
          </div>
          <div class="modal-body">
              <video width="960" height="540" controls>
                <source v-for="videoVersion in videoVersions"
                        :key="videoVersion.type"
                        :src="videoVersion.url"
                        :type="videoVersion.type">
                La vidéo ne fonctionne pas avec votre navigateur.
              </video>
          </div>
        </div>
      </div>
    </div>
</template>

<script>
import '../../css/utils.css'
import { defineComponent } from 'vue'

export default defineComponent({
  name: 'MyComponent', // nom du composant facultatif mais conseillé
  props: {
    videoVersions: Array,
  },
})
</script>
