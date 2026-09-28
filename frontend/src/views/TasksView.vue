<template>
  <div class="min-h-screen bg-slate-200">
    <!-- Header -->
    <header class="bg-slate-900 shadow-lg sticky top-0 z-20">
      <div class="max-w-6xl mx-auto px-4 py-4 flex items-center justify-between">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 rounded-xl bg-indigo-500 flex items-center justify-center shadow-md">
            <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
            </svg>
          </div>
          <div>
            <h1 class="text-lg font-bold text-white leading-tight">My Tasks</h1>
            <p class="text-xs text-slate-400">
              Signed in as <span class="font-medium text-slate-200">{{ authStore.user?.username }}</span>
            </p>
          </div>
        </div>
        <button
          @click="authStore.logout"
          class="text-sm font-medium text-slate-300 hover:text-white border border-slate-700 hover:border-slate-500 hover:bg-slate-800 rounded-lg px-3 py-1.5 transition"
        >
          Logout
        </button>
      </div>
    </header>

    <main class="max-w-6xl mx-auto px-4 py-6 grid grid-cols-1 lg:grid-cols-[380px_1fr] gap-6 items-start">
      <!-- ЛЕВАЯ КОЛОНКА: форма создания, sticky -->
      <aside class="lg:sticky lg:top-24">
        <form
          @submit.prevent="createTask"
          class="bg-white rounded-2xl shadow-lg border-l-4 border-indigo-500 p-5 space-y-4"
        >
          <div>
            <h2 class="text-base font-bold text-slate-900">New task</h2>
            <p class="text-xs text-slate-500 mt-0.5">Add a task to your list</p>
          </div>

          <div>
            <label class="block text-xs font-semibold text-slate-600 uppercase tracking-wide mb-1.5">
              Title
            </label>
            <input
              v-model="newTask.title"
              type="text"
              required
              maxlength="30"
              placeholder="What needs to be done?"
              class="w-full px-3 py-2.5 bg-slate-100 border-2 border-slate-200 rounded-lg text-slate-900 text-sm placeholder-slate-400 focus:outline-none focus:border-indigo-500 focus:bg-white transition"
            />
          </div>

          <div>
            <label class="block text-xs font-semibold text-slate-600 uppercase tracking-wide mb-1.5">
              Description <span class="text-slate-400 normal-case font-normal">(optional)</span>
            </label>
            <textarea
              v-model="newTask.description"
              maxlength="500"
              rows="4"
              placeholder="Add more details…"
              class="w-full px-3 py-2.5 bg-slate-100 border-2 border-slate-200 rounded-lg text-slate-900 text-sm placeholder-slate-400 focus:outline-none focus:border-indigo-500 focus:bg-white transition resize-none"
            ></textarea>
          </div>

          <button
            type="submit"
            :disabled="creating || !newTask.title.trim()"
            class="w-full bg-indigo-600 hover:bg-indigo-700 disabled:bg-slate-300 disabled:cursor-not-allowed text-white font-semibold px-4 py-2.5 rounded-lg shadow-md hover:shadow-lg transition"
          >
            {{ creating ? 'Adding…' : '+ Add task' }}
          </button>
        </form>

        <!-- Счётчик -->
        <div class="mt-4 px-5 py-3 bg-slate-800 rounded-xl shadow-md flex items-center justify-between">
          <span class="text-xs font-medium text-slate-400 uppercase tracking-wide">Total tasks</span>
          <span class="text-2xl font-bold text-white">{{ tasks.length }}</span>
        </div>
      </aside>

      <!-- ПРАВАЯ КОЛОНКА: список -->
      <section>
        <div v-if="loadingTasks" class="text-center text-slate-500 py-12">Loading…</div>

        <div
          v-else-if="!tasks.length"
          class="bg-white rounded-2xl shadow-lg border-l-4 border-slate-300 p-12 text-center"
        >
          <div class="w-14 h-14 mx-auto mb-3 rounded-full bg-slate-100 flex items-center justify-center">
            <svg class="w-7 h-7 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
            </svg>
          </div>
          <p class="text-slate-700 font-semibold">No tasks yet</p>
          <p class="text-sm text-slate-500 mt-1">Create your first one on the left</p>
        </div>

        <ul v-else class="space-y-2">
          <TaskItem
            v-for="task in tasks"
            :key="task.oid"
            :task="task"
            @updated="onTaskUpdated"
            @delete="deleteTask"
          />
        </ul>
      </section>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import TaskItem from '@/components/TaskItem.vue'
import { tasksApi } from '@/api/tasks'
import { useAuthStore } from '@/stores/auth'
import type { TaskCreate, TaskResponse } from '@/types/api'

const authStore = useAuthStore()
const tasks = ref<TaskResponse[]>([])
const newTask = ref<TaskCreate>({ title: '', description: '' })
const creating = ref(false)
const loadingTasks = ref(false)

async function fetchTasks() {
  loadingTasks.value = true
  try {
    tasks.value = await tasksApi.list()
  } finally {
    loadingTasks.value = false
  }
}

async function createTask() {
  creating.value = true
  try {
    await tasksApi.create(newTask.value)
    newTask.value = { title: '', description: '' }
    await fetchTasks()
  } finally {
    creating.value = false
  }
}

function onTaskUpdated(updated: TaskResponse) {
  const idx = tasks.value.findIndex((t) => t.oid === updated.oid)
  if (idx !== -1) tasks.value[idx] = updated
}

async function deleteTask(oid: string) {
  if (!confirm('Delete this task?')) return
  await tasksApi.remove(oid)
  tasks.value = tasks.value.filter((t) => t.oid !== oid)
}

onMounted(fetchTasks)
</script>