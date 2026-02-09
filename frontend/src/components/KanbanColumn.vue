<template>
  <div class="flex h-full flex-col rounded-2xl border border-slate-200 bg-white/60">
    <div class="flex items-center justify-between px-4 py-3">
      <div class="flex items-center gap-2">
        <span class="text-sm font-semibold text-slate-900">{{ title }}</span>
        <span class="rounded-full bg-slate-100 px-2 py-0.5 text-xs font-medium text-slate-700">
          {{ tasks.length }}
        </span>
      </div>
      <button
        class="rounded-xl bg-slate-900 px-3 py-1.5 text-xs font-medium text-white hover:bg-slate-800"
        type="button"
        @click="$emit('create')"
      >
        + 新建
      </button>
    </div>

    <div class="px-3 pb-3">
      <VueDraggable
        v-model="tasks"
        class="flex min-h-[120px] flex-col gap-3"
        group="tasks"
        :animation="180"
        ghost-class="opacity-40"
        drag-class="shadow-lg"
        @end="$emit('drag-end')"
      >
        <div v-for="t in tasks" :key="t.id">
          <TaskCard
            :task="t"
            @edit="$emit('edit', t)"
            @delete="$emit('delete', t)"
          />
        </div>
      </VueDraggable>

      <div v-if="!tasks.length" class="mt-3 rounded-xl border border-dashed border-slate-200 p-4 text-center text-sm text-slate-500">
        这里还没有任务
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { VueDraggable } from 'vue-draggable-plus'

import type { Task } from '@/types'
import TaskCard from './TaskCard.vue'

defineProps<{
  title: string
}>()

defineEmits<{
  (e: 'create'): void
  (e: 'edit', task: Task): void
  (e: 'delete', task: Task): void
  (e: 'drag-end'): void
}>()

// 用 v-model 传入可写数组，避免直接修改 props（会导致某些环境下不渲染/不更新）
const tasks = defineModel<Task[]>({ required: true })
</script>

