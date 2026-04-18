<template>
  <div class="gp-table-wrapper">
    <table class="gp-table">
      <thead>
        <tr>
          <th v-for="col in columns" :key="col.key" :style="{ width: col.width }">
            {{ col.label }}
          </th>
          <th v-if="hasActions" style="width: 100px">Ações</th>
        </tr>
      </thead>
      <tbody>
        <tr v-if="loading">
          <td :colspan="columns.length + (hasActions ? 1 : 0)" class="loading-cell">
            Carregando...
          </td>
        </tr>
        <tr v-else-if="!data.length">
          <td :colspan="columns.length + (hasActions ? 1 : 0)" class="empty-cell">
            {{ emptyMessage }}
          </td>
        </tr>
        <tr v-else v-for="(row, idx) in data" :key="row.id || idx">
          <td v-for="col in columns" :key="col.key">
            <slot :name="col.key" :row="row" :value="row[col.key]">
              {{ row[col.key] }}
            </slot>
          </td>
          <td v-if="hasActions" class="actions-cell">
            <slot name="actions" :row="row"></slot>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  data: { type: Array, default: () => [] },
  columns: { type: Array, required: true },
  loading: { type: Boolean, default: false },
  emptyMessage: { type: String, default: 'Nenhum registro encontrado' },
  hasActions: { type: Boolean, default: true }
})
</script>

<style scoped>
.gp-table-wrapper {
  overflow-x: auto;
}

.gp-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
}

.gp-table th {
  text-align: left;
  padding: 12px 16px;
  background: rgba(99, 102, 241, 0.1);
  color: #818cf8;
  font-weight: 600;
  white-space: nowrap;
}

.gp-table td {
  padding: 12px 16px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  color: #e2e8f0;
}

.gp-table tr:hover td {
  background: rgba(255, 255, 255, 0.02);
}

.loading-cell, .empty-cell {
  text-align: center;
  padding: 40px;
  color: rgba(255, 255, 255, 0.5);
}

.actions-cell {
  text-align: center;
}
</style>