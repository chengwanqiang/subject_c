import { defineStore } from 'pinia'

import { api } from '@/lib/api'
import type { Task, TaskStatus } from '@/types'

type Columns = Record<TaskStatus, Task[]>

function emptyColumns(): Columns {
  return { todo: [], doing: [], done: [] }
}

function sortByPosition(a: Task, b: Task) {
  if (a.position !== b.position) return a.position - b.position
  return a.id - b.id
}

export const useTasksStore = defineStore('tasks', {
  state: () => ({
    loading: false as boolean,
    columns: emptyColumns() as Columns,
  }),
  actions: {
    async fetchAll() {
      this.loading = true
      try {
        const { data } = await api.get<Task[]>('/tasks')
        const cols = emptyColumns()
        for (const t of data) cols[t.status].push(t)
        cols.todo.sort(sortByPosition)
        cols.doing.sort(sortByPosition)
        cols.done.sort(sortByPosition)
        this.columns = cols
      } finally {
        this.loading = false
      }
    },
    async createTask(input: { title: string; description: string; status: TaskStatus }) {
      const { data } = await api.post<Task>('/tasks', input)
      this.columns[data.status].push(data)
      this.columns[data.status].sort(sortByPosition)
      return data
    },
    async updateTask(taskId: number, patch: Partial<Pick<Task, 'title' | 'description' | 'status' | 'position'>>) {
      const { data } = await api.patch<Task>(`/tasks/${taskId}`, patch)
      // 直接刷新列，保证移动/排序后状态一致
      await this.fetchAll()
      return data
    },
    async deleteTask(taskId: number) {
      await api.delete(`/tasks/${taskId}`)
      await this.fetchAll()
    },
    async reorder() {
      const payload = {
        columns: {
          todo: this.columns.todo.map((t) => t.id),
          doing: this.columns.doing.map((t) => t.id),
          done: this.columns.done.map((t) => t.id),
        },
      }
      await api.post('/tasks/reorder', payload)
      // 服务端会把 position 写入数据库；本地也同步 position，避免刷新前排序抖动
      ;(['todo', 'doing', 'done'] as const).forEach((status) => {
        this.columns[status].forEach((t, idx) => {
          t.status = status
          t.position = idx
        })
      })
    },
  },
})

