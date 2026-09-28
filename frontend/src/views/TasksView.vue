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
          @click="handleLogout"
          class="text-sm font-medium text-slate-300 hover:text-white border border-slate-700 hover:border-slate-500 hover:bg-slate-800 rounded-lg px-3 py-1.5 transition"
        >
          Logout
        </button>
      </div>
    </header>

    <main class="max-w-6xl mx-auto px-4 py-6 grid grid-cols-1 lg:grid-cols-[380px_1fr] gap-6 items-start">
      <!-- ЛЕВАЯ КОЛОНКА -->
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

        <!-- Статистика -->
        <div class="mt-4 grid grid-cols-3 gap-2">
          <div class="bg-white rounded-xl shadow-sm border border-slate-200 px-3 py-2.5 text-center">
            <p class="text-[10px] font-semibold text-slate-500 uppercase tracking-wide">Total</p>
            <p class="text-xl font-bold text-slate-900">{{ stats.total }}</p>
          </div>
          <div class="bg-white rounded-xl shadow-sm border border-slate-200 px-3 py-2.5 text-center">
            <p class="text-[10px] font-semibold text-indigo-600 uppercase tracking-wide">Active</p>
            <p class="text-xl font-bold text-indigo-600">{{ stats.active }}</p>
          </div>
          <div class="bg-white rounded-xl shadow-sm border border-slate-200 px-3 py-2.5 text-center">
            <p class="text-[10px] font-semibold text-slate-500 uppercase tracking-wide">Done</p>
            <p class="text-xl font-bold text-slate-400">{{ stats.done }}</p>
          </div>
        </div>
      </aside>

      <!-- ПРАВАЯ КОЛОНКА -->
      <section class="space-y-4">
        <!-- Панель поиска и фильтров -->
        <div class="bg-white rounded-2xl shadow-lg border border-slate-200 p-4 space-y-3">
          <!-- Поиск -->
          <div class="relative">
            <svg
              class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400 pointer-events-none"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
            <input
              v-model="search"
              type="text"
              placeholder="Search by title or description…"
              class="w-full pl-9 pr-9 py-2.5 bg-slate-100 border-2 border-slate-200 rounded-lg text-slate-900 text-sm placeholder-slate-400 focus:outline-none focus:border-indigo-500 focus:bg-white transition"
            />
            <button
              v-if="search"
              @click="search = ''"
              class="absolute right-2 top-1/2 -translate-y-1/2 w-6 h-6 flex items-center justify-center rounded-md text-slate-400 hover:text-slate-700 hover:bg-slate-200 transition"
              title="Clear"
            >
              <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          <!-- Фильтр-таблетки -->
          <div class="flex gap-1.5">
            <button
              v-for="option in filterOptions"
              :key="option.value"
              @click="filter = option.value"
              class="flex-1 px-3 py-2 rounded-lg text-xs font-semibold transition border-2"
              :class="
                filter === option.value
                  ? 'bg-indigo-600 border-indigo-600 text-white shadow-sm'
                  : 'bg-white border-slate-200 text-slate-600 hover:border-indigo-300 hover:text-indigo-600'
              "
            >
              {{ option.label }}
              <span
                class="ml-1 px-1.5 py-0.5 rounded text-[10px]"
                :class="
                  filter === option.value
                    ? 'bg-white/20 text-white'
                    : 'bg-slate-100 text-slate-500'
                "
              >
                {{ option.count }}
              </span>
            </button>
          </div>
        </div>

        <!-- Loading / Empty -->
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

        <!-- Ничего не найдено -->
        <div
          v-else-if="!visibleTasks.length"
          class="bg-white rounded-2xl shadow-lg border-l-4 border-amber-400 p-12 text-center"
        >
          <div class="w-14 h-14 mx-auto mb-3 rounded-full bg-amber-50 flex items-center justify-center">
            <svg class="w-7 h-7 text-amber-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          </div>
          <p class="text-slate-700 font-semibold">Nothing found</p>
          <p class="text-sm text-slate-500 mt-1">
            Try a different search or filter
          </p>
          <button
            @click="resetFilters"
            class="mt-3 text-xs font-semibold text-indigo-600 hover:text-indigo-700 hover:bg-indigo-50 rounded-lg px-3 py-1.5 transition"
          >
            Reset filters
          </button>
        </div>

        <!-- Список -->
        <ul v-else class="space-y-2">
          <TaskItem
            v-for="task in visibleTasks"
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
import { ref, computed, onMounted } from 'vue'
import TaskItem from '@/components/TaskItem.vue'
import { tasksApi } from '@/api/tasks'
import { useAuthStore } from '@/stores/auth'
import type { TaskCreate, TaskResponse } from '@/types/api'
import { useRouter } from 'vue-router'
type FilterValue = 'all' | 'active' | 'done'

const authStore = useAuthStore()
const router = useRouter()
const tasks = ref<TaskResponse[]>([])
const newTask = ref<TaskCreate>({ title: '', description: '' })
const creating = ref(false)
const loadingTasks = ref(false)

const search = ref('')
const filter = ref<FilterValue>('all')

const stats = computed(() => ({
  total: tasks.value.length,
  active: tasks.value.filter((t) => !t.is_done).length,
  done: tasks.value.filter((t) => t.is_done).length,
}))

const filterOptions = computed(() => [
  { value: 'all' as const, label: 'All', count: stats.value.total },
  { value: 'active' as const, label: 'Active', count: stats.value.active },
  { value: 'done' as const, label: 'Done', count: stats.value.done },
])

const visibleTasks = computed(() => {
  const q = search.value.trim().toLowerCase()

  return tasks.value.filter((task) => {
    // фильтр по статусу
    if (filter.value === 'active' && task.is_done) return false
    if (filter.value === 'done' && !task.is_done) return false

    // поиск
    if (!q) return true
    const inTitle = task.title.toLowerCase().includes(q)
    const inDescription = (task.description ?? '').toLowerCase().includes(q)
    return inTitle || inDescription
  })
})

function resetFilters() {
  search.value = ''
  filter.value = 'all'
}

function handleLogout() {
  authStore.logout()
  router.push({ name: 'login' })
}

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