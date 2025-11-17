<template>
  <div class="container py-4">

    <!-- TITRE -->
    <h2 class="mb-4">
      <i class="fas fa-folder-open me-2"></i>
      Détails du contrôle
    </h2>

    <!-- FORMULAIRE -->
    <form @submit.prevent="saveForm" class="card p-3 shadow-sm mb-4">

      <div class="row mb-3">
        <div class="col-md-6">
          <label class="form-label">Intitulé</label>
          <input v-model="form.intitule" type="text" class="form-control" required>
        </div>

        <div class="col-md-6">
          <label class="form-label">Référence</label>
          <input v-model="form.reference" type="text" class="form-control">
        </div>
      </div>

      <div class="row mb-3">
        <div class="col-md-4">
          <label class="form-label">Date début</label>
          <input v-model="form.date_debut" type="date" class="form-control">
        </div>

        <div class="col-md-4">
          <label class="form-label">Date fin</label>
          <input v-model="form.date_fin" type="date" class="form-control">
        </div>

        <div class="col-md-4">
          <label class="form-label">Statut</label>
          <select v-model="form.statut" class="form-select">
            <option value="en_cours">En cours</option>
            <option value="termine">Terminé</option>
            <option value="en_pause">En pause</option>
          </select>
        </div>
      </div>

      <button class="btn btn-primary">
        <i class="fas fa-save me-2"></i> Enregistrer
      </button>
    </form>

    <!-- DROPZONE UPLOAD -->
    <div class="card p-3 shadow-sm mb-4">
      <h5 class="mb-3">
        <i class="fas fa-upload me-2"></i> Upload des pièces jointes
      </h5>

      <form id="myDropzone" class="dropzone"></form>
    </div>

    <!-- TABLEAU -->
    <div class="card p-3 shadow-sm">
      <h5 class="mb-3">
        <i class="fas fa-list me-2"></i> Documents liés
      </h5>

      <ads-table-tree
        :columns="columns"
        :rows="rows"
        :selectable="false"
      />
    </div>

  </div>
</template>

<script>
import { ref, onMounted } from "vue";
import Swal from "sweetalert2";

// Dropzone v5 (officielle)
import Dropzone from "dropzone";
import "dropzone/dist/dropzone.css";

// vue-ads-table-tree v2.1.7 compatible Vue 3
//import AdsTableTree from "vue-ads-table-tree";

export default {
  name: "ControlDetails",
  components: {
    //AdsTableTree,
  },

  setup() {
    // -----------------------------
    // Formulaire
    // -----------------------------
    const form = ref({
      intitule: "",
      reference: "",
      date_debut: "",
      date_fin: "",
      statut: "en_cours",
    });

    const saveForm = () => {
      Swal.fire({
        title: "Enregistré",
        icon: "success",
        timer: 1200,
        showConfirmButton: false,
      });
    };

    // -----------------------------
    // Tableau de documents
    // -----------------------------
    const columns = ref([
      { property: "name", label: "Nom", width: 250 },
      { property: "type", label: "Type", width: 120 },
      { property: "size", label: "Taille", width: 100 },
    ]);

    const rows = ref([
      {
        id: 1,
        name: "Rapport.pdf",
        type: "PDF",
        size: "220 Ko",
        children: [
          { id: 2, name: "Annexe 1.xlsx", type: "Excel", size: "85 Ko" },
        ],
      },
    ]);

    // -----------------------------
    // Dropzone
    // -----------------------------
    onMounted(() => {
      Dropzone.autoDiscover = false;

      new Dropzone("#myDropzone", {
        url: "/upload",     // Endpoint backend
        maxFilesize: 20,    // MB
        timeout: 0,
        dictDefaultMessage: "Déposez vos fichiers ici",
        init() {
          this.on("success", (file, response) => {
            Swal.fire({
              title: "Fichier uploadé",
              text: file.name,
              icon: "success",
              timer: 1200,
              showConfirmButton: false,
            });
          });

          this.on("error", (file, errorMessage) => {
            Swal.fire({
              title: "Erreur",
              text: errorMessage,
              icon: "error",
            });
          });
        },
      });
    });

    return {
      form,
      saveForm,
      columns,
      rows,
    };
  },
};
</script>

<style scoped>
.card {
  border-radius: 12px;
}

.dropzone {
  border: 2px dashed #6c757d !important;
  background: #fafafa;
  padding: 30px;
  border-radius: 10px;
}
</style>
