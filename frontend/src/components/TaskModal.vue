<template>
  <div v-if="open" class="fixed inset-0 z-50">
    <div class="absolute inset-0 bg-black/30" @click="close"></div>

    <div class="absolute inset-0 flex items-center justify-center p-4">
      <div class="w-full max-w-lg rounded-2xl bg-white shadow-xl">
        <div class="flex items-center justify-between border-b border-slate-100 px-5 py-4">
          <div class="text-base font-semibold text-slate-900">
            {{ mode === 'create' ? '新建任务' : '编辑任务' }}
          </div>
          <button
            class="rounded-lg px-2 py-1 text-sm text-slate-600 hover:bg-slate-100"
            type="button"
            @click="close"
          >
            关闭
          </button>
        </div>

        <form class="px-5 py-4" @submit.prevent="submit">
          <label class="block text-sm font-medium text-slate-700">标题</label>
          <input
            v-model.trim="draft.title"
            class="mt-2 w-full rounded-xl border border-slate-200 px-3 py-2 outline-none focus:border-slate-400"
            placeholder="例如：实现登录页 UI"
            required
          />

          <label class="mt-4 block text-sm font-medium text-slate-700">描述</label>
          <textarea
            v-model.trim="draft.description"
            rows="4"
            class="mt-2 w-full resize-none rounded-xl border border-slate-200 px-3 py-2 outline-none focus:border-slate-400"
            placeholder="补充一些细节（可选）"
          />

          <label class="mt-4 block text-sm font-medium text-slate-700">状态</label>
          <select
            v-model="draft.status"
            class="mt-2 w-full rounded-xl border border-slate-200 px-3 py-2 outline-none focus:border-slate-400"
          >
            <option value="todo">Todo</option>
            <option value="doing">Doing</option>
            <option value="done">Done</option>
          </select>

          <div class="mt-6 flex items-center justify-end gap-2">
            <button
              class="rounded-xl px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-100"
              type="button"
              @click="close"
            >
              取消
            </button>
            <button
              class="rounded-xl bg-slate-900 px-4 py-2 text-sm font-medium text-white hover:bg-slate-800 disabled:opacity-60"
              type="submit"
              :disabled="!draft.title"
            >
              {{ mode === 'create' ? '创建' : '保存' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, watch } from 'vue'
import type { Task, TaskStatus } from '@/types'

const props = defineProps<{
  open: boolean
  mode: 'create' | 'edit'
  initial?: Partial<Pick<Task, 'id' | 'title' | 'description' | 'status'>>
}>()

const emit = defineEmits<{
  (e: 'close'): void
  (e: 'submit', payload: { id?: number; title: string; description: string; status: TaskStatus }): void
}>()

const draft = reactive<{ id?: number; title: string; description: string; status: TaskStatus }>({
  id: undefined,
  title: '',
  description: '',
  status: 'todo',
})

watch(
  () => [props.open, props.initial] as const,
  () => {
    if (!props.open) return
    draft.id = props.initial?.id
    draft.title = props.initial?.title ?? ''
    draft.description = props.initial?.description ?? ''
    draft.status = (props.initial?.status as TaskStatus) ?? 'todo'
  },
  { immediate: true },
)

function close() {
  emit('close')
}

function submit() {
  emit('submit', {
    id: draft.id,
    title: draft.title,
    description: draft.description,
    status: draft.status,
  })
}
</script>

