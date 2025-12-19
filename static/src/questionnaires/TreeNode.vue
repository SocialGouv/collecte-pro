<template>
  <tr class="tree-row" :class="{ selected: isSelected }">
    <td class="col-expand">
      <button 
        v-if="node._children && node._children.length > 0"
        @click="$emit('toggle', node.id)"
        class="expand-btn"
        type="button"
      >
        <span v-if="node._showChildren" class="fe fe-folder-minus" aria-hidden="true"></span>
        <span v-else class="fe fe-folder-plus" aria-hidden="true"></span>
      </button>
    </td>
    
    <td class="col-checkbox">
      <input 
        v-if="node._id && node._id.startsWith('file')"
        type="checkbox" 
        :checked="isSelected"
        @change="$emit('select', node)"
        class="node-checkbox"
      />
    </td>

    <td class="col-document" :class="'node-' + node._id">
      <div class="doc-content" :style="{ marginLeft: indentLevel + 'px' }">
        <template v-if="node._id === 'file'">
          <a :href="node.url" target="_blank" rel="noopener noreferrer" class="btn tag tag-azure pull-left btn-file" :title="node.name">
            {{ node.short_name }}
            <span class="tag-addon pb-1"><span class="fe fe-file" aria-hidden="true"></span></span>
          </a>
        </template>
        <template v-else-if="node._id === 'fileAnnexe'">
          <a :href="node.url" target="_blank" rel="noopener noreferrer" class="btn tag tag-orange pull-left btn-file" :title="node.name">
            {{ node.short_name }}
            <span class="tag-addon pb-1"><span class="fe fe-paperclip" aria-hidden="true"></span></span>
          </a>
        </template>
        <template v-else-if="node._id === 'filePieceJointe'">
          <a :href="node.url" target="_blank" rel="noopener noreferrer" class="btn tag tag-orange pull-left btn-file" :title="node.name">
            {{ node.short_name }}
            <span class="tag-addon pb-1"><span class="fe fe-paperclip" aria-hidden="true"></span></span>
          </a>
        </template>
        <template v-else-if="node._id === 'fileCorbeille'">
          <a :href="node.url" target="_blank" rel="noopener noreferrer" class="btn tag tag-azure pull-left btn-file" :title="node.name">
            {{ node.short_name }}
            <span class="tag-addon pb-1"><span class="fe fe-trash-2" aria-hidden="true"></span></span>
          </a>
        </template>
        <template v-else>
          <span class="folder-icon">📁</span>
          <strong>{{ node.name }}</strong>
        </template>
      </div>
    </td>

    <td class="col-date">{{ showDate ? node.dateDepot : '' }}</td>
    <td class="col-repondant">{{ showRepondant ? node.repondant : '' }}</td>
  </tr>

  <template v-if="node._showChildren && node._children && node._children.length > 0">
    <TreeNode 
      v-for="child in node._children"
      :key="child.id"
      :node="child"
      :selected="selected"
      :depth="depth + 1"
      @toggle="$emit('toggle', $event)"
      @select="$emit('select', $event)"
    />
  </template>
</template>

<script lang="ts">
import { defineComponent, PropType, computed } from 'vue'

export default defineComponent({
  name: 'TreeNode',
  props: {
    node: { type: Object as PropType<any>, required: true },
    selected: { type: Array as PropType<any[]>, default: () => [] },
    depth: { type: Number, default: 0 }
  },
  emits: ['toggle', 'select'],
  setup(props) {
    const isSelected = computed(() => {
      return props.selected.some((item: any) => item && item.id === props.node.id)
    })

    const indentLevel = computed(() => {
      return props.depth * 24
    })

    const showDate = computed(() => {
      return props.node._id && props.node._id.startsWith('file')
    })

    const showRepondant = computed(() => {
      return props.node._id && props.node._id.startsWith('file')
    })

    return { isSelected, indentLevel, showDate, showRepondant }
  }
})
</script>

<style scoped>
.tree-row {
  border-bottom: 1px solid #e9ecef;
}

.tree-row.selected {
  background-color: #f8f9fa;
}

.tree-row td {
  padding: 4px 8px;
  vertical-align: middle;
}

.col-expand {
  width: 30px;
  text-align: center;
  border: none;
}

.expand-btn {
  background: none;
  border: none;
  cursor: pointer;
  padding: 0;
  color: #6c757d;
}

.col-checkbox {
  width: 32px;
  text-align: center;
  border: none;
}

.node-checkbox {
  cursor: pointer;
}

.col-document {
  width: 550px;
  border-right: 1px solid #dee2e6;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 550px;
  word-break: break-word;
}

.col-document a.btn-file {
  display: inline-block;
}

.col-date {
  width: 160px;
  border-right: 1px solid #dee2e6;
  font-size: 0.85rem;
  color: #6c757d;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.col-repondant {
  width: 150px;
  font-size: 0.85rem;
  color: #6c757d;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.node-theme,
.node-question {
  font-weight: 500;
  color: #495057;
}

.node-questionnaire {
  font-weight: bold;
  color: #212529;
}

.node-annexes,
.node-piecesjointes,
.node-corbeille {
  font-weight: 500;
  color: #0c5460;
  background-color: #d1ecf1;
  padding: 2px 6px;
  border-radius: 3px;
}

.doc-content {
  display: flex;
  align-items: center;
  gap: 8px;
}

.folder-icon {
  display: inline-block;
  width: 16px;
  height: 16px;
  font-size: 14px;
}
</style>
