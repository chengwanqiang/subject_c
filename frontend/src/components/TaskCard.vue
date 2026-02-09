<template>
  <div
    class="relative rounded-xl border border-slate-200 bg-white p-3 shadow-sm hover:shadow transition-shadow"
    @dblclick="$emit('edit')"
  >
    <div class="flex items-start justify-between gap-2">
      <div class="min-w-0">
        <div class="truncate font-medium text-slate-900">
          {{ task.title }}
        </div>
        <div v-if="task.description" class="mt-1 line-clamp-3 text-sm text-slate-600">
          {{ task.description }}
        </div>
      </div>
    </div>

    <div class="absolute right-2 top-2 flex gap-1 rounded-xl border border-slate-200 bg-white/90 p-1 backdrop-blur">
      <button
        class="rounded-lg px-2 py-1 text-xs font-medium text-slate-700 hover:bg-slate-100"
        type="button"
        @click="$emit('edit')"
        title="编辑（也可双击卡片）"
      >
        编辑
      </button>
      <button
        class="rounded-lg px-2 py-1 text-xs font-medium text-rose-700 hover:bg-rose-50"
        type="button"
        @click="$emit('delete')"
        title="删除"
      >
        删除
      </button>
    </div>

    <div class="mt-3 flex items-center justify-between text-xs text-slate-400">
      <span>#{{ task.id }}</span>
      <span>{{ updatedAtText }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { Task } from '@/types'
import { computed } from 'vue'

const props = defineProps<{
  task: Task
}>()

defineEmits<{
  (e: 'edit'): void
  (e: 'delete'): void
}>()

function formatTime(iso: string) {
  const d = new Date(iso)
  if (Number.isNaN(d.getTime())) return ''
  return d.toLocaleString()
}

const updatedAtText = computed(() => formatTime(props.task.updated_at))
</script>

<style scoped>
.line-clamp-3 {
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>

