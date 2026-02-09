<template>
  <div class="min-h-screen">
    <header class="sticky top-0 z-10 border-b border-slate-200 bg-white/80 backdrop-blur">
      <div class="mx-auto flex max-w-6xl items-center justify-between px-4 py-4">
        <div class="flex items-center gap-3">
          <div class="grid h-10 w-10 place-items-center rounded-2xl bg-slate-900 text-white">
            K
          </div>
          <div>
            <div class="text-base font-semibold leading-tight text-slate-900">Kanban Board</div>
            <div class="text-xs text-slate-500">Todo / Doing / Done，支持拖拽并持久化到 MySQL</div>
          </div>
        </div>

        <div class="flex items-center gap-2">
          <button
            class="rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm font-medium text-slate-800 hover:bg-slate-50"
            type="button"
            @click="refresh"
            :disabled="store.loading"
          >
            刷新
          </button>
          <button
            class="rounded-xl bg-slate-900 px-3 py-2 text-sm font-medium text-white hover:bg-slate-800"
            type="button"
            @click="openCreate('todo')"
          >
            新建任务
          </button>
        </div>
      </div>
    </header>

    <main class="mx-auto max-w-6xl px-4 py-6">
      <div v-if="store.loading" class="mb-4 rounded-2xl border border-slate-200 bg-white p-4 text-sm text-slate-600">
        正在加载任务…
      </div>

      <div class="grid gap-4 md:grid-cols-3">
        <KanbanColumn
          title="Todo"
          v-model="store.columns.todo"
          @create="openCreate('todo')"
          @edit="openEdit"
          @delete="onDelete"
          @drag-end="onDragEnd"
        />
        <KanbanColumn
          title="Doing"
          v-model="store.columns.doing"
          @create="openCreate('doing')"
          @edit="openEdit"
          @delete="onDelete"
          @drag-end="onDragEnd"
        />
        <KanbanColumn
          title="Done"
          v-model="store.columns.done"
          @create="openCreate('done')"
          @edit="openEdit"
          @delete="onDelete"
          @drag-end="onDragEnd"
        />
      </div>

      <div class="mt-6 rounded-2xl border border-slate-200 bg-white p-4 text-sm text-slate-600">
        <div class="font-medium text-slate-900">使用提示</div>
        <ul class="mt-2 list-disc space-y-1 pl-5">
          <li>拖拽卡片在列内排序，或跨列移动（Todo/Doing/Done）。</li>
          <li>拖拽结束会自动调用接口保存顺序与状态。</li>
          <li>默认通过 Nginx 反代，前端请求的 <code>/api</code> 会转到后端容器。</li>
        </ul>
      </div>
    </main>

    <TaskModal
      :open="modal.open"
      :mode="modal.mode"
      :initial="modal.initial"
      @close="modal.open = false"
      @submit="onModalSubmit"
    />
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive } from 'vue'

import KanbanColumn from '@/components/KanbanColumn.vue'
import TaskModal from '@/components/TaskModal.vue'
import { useTasksStore } from '@/stores/tasks'
import type { Task, TaskStatus } from '@/types'

const store = useTasksStore()

const modal = reactive<{
  open: boolean
  mode: 'create' | 'edit'
  initial?: Partial<Pick<Task, 'id' | 'title' | 'description' | 'status'>>
}>({
  open: false,
  mode: 'create',
  initial: undefined,
})

onMounted(async () => {
  await store.fetchAll()
})

async function refresh() {
  await store.fetchAll()
}

function openCreate(status: TaskStatus) {
  modal.mode = 'create'
  modal.initial = { title: '', description: '', status }
  modal.open = true
}

function openEdit(task: Task) {
  modal.mode = 'edit'
  modal.initial = { id: task.id, title: task.title, description: task.description, status: task.status }
  modal.open = true
}

async function onModalSubmit(payload: { id?: number; title: string; description: string; status: TaskStatus }) {
  try {
    if (modal.mode === 'create') {
      await store.createTask({ title: payload.title, description: payload.description, status: payload.status })
    } else if (payload.id != null) {
      await store.updateTask(payload.id, { title: payload.title, description: payload.description, status: payload.status })
    }
    modal.open = false
  } catch (e) {
    alert(`操作失败：${String(e)}`)
  }
}

async function onDelete(task: Task) {
  const ok = confirm(`确定删除任务 #${task.id} 吗？`)
  if (!ok) return
  try {
    await store.deleteTask(task.id)
  } catch (e) {
    alert(`删除失败：${String(e)}`)
  }
}

let reorderLock = false
async function onDragEnd() {
  // 避免连续触发导致并发请求
  if (reorderLock) return
  reorderLock = true
  try {
    await store.reorder()
  } catch (e) {
    alert(`保存拖拽结果失败：${String(e)}`)
    await store.fetchAll()
  } finally {
    reorderLock = false
  }
}
</script>

