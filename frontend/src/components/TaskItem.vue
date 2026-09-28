<template>
  <li
    class="bg-white rounded-lg shadow-sm border border-slate-200 hover:border-indigo-400 hover:shadow-md transition overflow-hidden group"
    :class="{ 'opacity-60': task.is_done }"
  >
    <!-- View mode -->
    <div v-if="!isEditing" class="flex items-stretch">
      <!-- Цветная полоска: серая для done, индиго для active -->
      <div
        class="w-1 shrink-0 group-hover:w-1.5 transition-all"
        :class="task.is_done ? 'bg-slate-300' : 'bg-indigo-500'"
      ></div>

      <div class="flex-1 px-3 py-2.5 flex items-center gap-3 min-w-0">
        <!-- ЧЕКБОКС -->
        <button
          type="button"
          :disabled="toggling"
          :title="task.is_done ? 'Mark as not done' : 'Mark as done'"
          class="w-5 h-5 shrink-0 rounded-md border-2 flex items-center justify-center transition disabled:opacity-50"
          :class="
            task.is_done
              ? 'bg-indigo-600 border-indigo-600'
              : 'bg-white border-slate-300 hover:border-indigo-500'
          "
          @click="toggleDone"
        >
          <svg
            v-if="task.is_done"
            class="w-3 h-3 text-white"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7" />
          </svg>
        </button>

        <!-- Контент -->
        <div class="flex-1 min-w-0">
          <div class="flex items-center gap-2">
            <h3
              class="font-semibold text-sm truncate transition"
              :class="task.is_done ? 'text-slate-400 line-through' : 'text-slate-900'"
            >
              {{ task.title }}
            </h3>
            <span
              v-if="task.updated_at !== task.created_at"
              class="text-[10px] font-semibold text-indigo-600 bg-indigo-50 px-1.5 py-0.5 rounded uppercase tracking-wide shrink-0"
            >
              Edited
            </span>
          </div>
          <p
            v-if="task.description"
            class="text-xs mt-0.5 truncate transition"
            :class="task.is_done ? 'text-slate-400' : 'text-slate-500'"
            :title="task.description"
          >
            {{ task.description }}
          </p>
        </div>

        <!-- Дата -->
        <span class="hidden sm:block text-[11px] text-slate-400 shrink-0 tabular-nums">
          {{ formatDate(task.created_at) }}
        </span>

        <!-- Кнопки-иконки -->
        <div class="flex gap-1.5 shrink-0">
          <button
            @click="startEdit"
            title="Edit"
            class="w-8 h-8 flex items-center justify-center rounded-lg bg-indigo-100 text-indigo-600 hover:bg-indigo-600 hover:text-white shadow-sm hover:shadow-md transition"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
            </svg>
          </button>
          <button
            @click="emit('delete', task.oid)"
            title="Delete"
            class="w-8 h-8 flex items-center justify-center rounded-lg bg-red-100 text-red-600 hover:bg-red-600 hover:text-white shadow-sm hover:shadow-md transition"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
            </svg>
          </button>
        </div>
      </div>
    </div>

    <!-- Edit mode -->
    <form v-else @submit.prevent="save" class="p-3 space-y-2 border-l-4 border-indigo-500">
      <input
        v-model="draft.title"
        type="text"
        required
        maxlength="30"
        class="w-full px-3 py-2 bg-slate-100 border-2 border-slate-200 rounded-lg text-slate-900 text-sm focus:outline-none focus:border-indigo-500 focus:bg-white transition"
      />
      <textarea
        v-model="draft.description"
        maxlength="500"
        rows="2"
        placeholder="Description (optional)"
        class="w-full px-3 py-2 bg-slate-100 border-2 border-slate-200 rounded-lg text-slate-900 text-sm placeholder-slate-400 focus:outline-none focus:border-indigo-500 focus:bg-white transition resize-none"
      ></textarea>

      <label class="flex items-center gap-2 text-sm text-slate-700 cursor-pointer select-none">
        <input
          v-model="draft.is_done"
          type="checkbox"
          class="w-4 h-4 accent-indigo-600 cursor-pointer"
        />
        <span>Done</span>
      </label>

      <p v-if="error" class="text-xs text-red-700 bg-red-50 border-l-4 border-red-500 px-2 py-1.5 rounded">
        {{ error }}
      </p>

      <div class="flex gap-2">
        <button
          type="submit"
          :disabled="saving || !draft.title.trim()"
          class="bg-indigo-600 hover:bg-indigo-700 disabled:bg-slate-300 disabled:cursor-not-allowed text-white text-xs font-semibold px-3 py-1.5 rounded-md shadow-sm transition"
        >
          {{ saving ? 'Saving…' : 'Save' }}
        </button>
        <button
          type="button"
          @click="cancelEdit"
          :disabled="saving"
          class="text-xs font-semibold text-slate-600 hover:text-slate-900 bg-slate-100 hover:bg-slate-200 rounded-md px-3 py-1.5 transition"
        >
          Cancel
        </button>
      </div>
    </form>
  </li>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { tasksApi } from '@/api/tasks'
import type { TaskResponse } from '@/types/api'

const props = defineProps<{ task: TaskResponse }>()
const emit = defineEmits<{
  (e: 'updated', task: TaskResponse): void
  (e: 'delete', oid: string): void
}>()

const isEditing = ref(false)
const saving = ref(false)
const toggling = ref(false)
const error = ref('')

const draft = reactive({ title: '', description: '', is_done: false })

function startEdit() {
  draft.title = props.task.title
  draft.description = props.task.description ?? ''
  draft.is_done = props.task.is_done
  error.value = ''
  isEditing.value = true
}

function cancelEdit() {
  isEditing.value = false
  error.value = ''
}

async function toggleDone() {
  toggling.value = true
  try {
    const updated = await tasksApi.update(props.task.oid, {
      is_done: !props.task.is_done,
    })
    emit('updated', updated)
  } catch (e: any) {
    // можно показать тост, но для пет-проекта молча игнорируем
    console.error('toggle failed', e)
  } finally {
    toggling.value = false
  }
}

async function save() {
  saving.value = true
  error.value = ''
  try {
    const payload: { title?: string; description?: string; is_done?: boolean } = {}

    if (draft.title !== props.task.title) payload.title = draft.title

    const originalDesc = props.task.description ?? ''
    if (draft.description !== originalDesc) payload.description = draft.description

    if (draft.is_done !== props.task.is_done) payload.is_done = draft.is_done

    if (Object.keys(payload).length === 0) {
      isEditing.value = false
      return
    }

    const updated = await tasksApi.update(props.task.oid, payload)
    emit('updated', updated)
    isEditing.value = false
  } catch (e: any) {
    const detail = e.response?.data?.detail
    error.value =
      typeof detail === 'string'
        ? detail
        : Array.isArray(detail)
          ? detail.map((d: any) => d.msg).join(', ')
          : 'Failed to save'
  } finally {
    saving.value = false
  }
}

function formatDate(iso: string): string {
  const d = new Date(iso)
  return d.toLocaleDateString(undefined, {
    day: '2-digit',
    month: 'short',
    hour: '2-digit',
    minute: '2-digit',
  })
}
</script>