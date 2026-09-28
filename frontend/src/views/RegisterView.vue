<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-100 px-4">
    <div class="w-full max-w-md bg-white rounded-2xl shadow-lg p-8">
      <h1 class="text-3xl font-bold text-gray-900 mb-2">Create account</h1>
      <p class="text-gray-500 mb-6">Start tracking your tasks</p>

      <form @submit.prevent="handleRegister" class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Email</label>
          <input
            v-model="form.email"
            type="email"
            required
            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition"
            placeholder="you@example.com"
          />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Username</label>
          <input
            v-model="form.username"
            type="text"
            required
            minlength="3"
            maxlength="20"
            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition"
            placeholder="testuser"
          />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Password</label>
          <input
            v-model="form.password"
            type="password"
            required
            minlength="4"
            maxlength="20"
            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition"
            placeholder="••••••••"
          />
        </div>

        <button
          type="submit"
          :disabled="loading"
          class="w-full bg-primary-600 hover:bg-primary-700 disabled:bg-primary-300 text-white font-medium py-2.5 rounded-lg transition"
        >
          {{ loading ? 'Creating…' : 'Create account' }}
        </button>

        <p
          v-if="error"
          class="text-sm text-red-600 bg-red-50 border border-red-200 rounded-lg px-3 py-2"
        >
          {{ error }}
        </p>
      </form>

      <p class="text-center text-sm text-gray-500 mt-6">
        Already have an account?
        <RouterLink to="/login" class="text-primary-600 hover:underline font-medium">
          Log in
        </RouterLink>
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter, RouterLink } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import type { UserCreate } from '@/types/api'

const form = reactive<UserCreate>({ email: '', username: '', password: '' })
const loading = ref(false)
const error = ref('')
const router = useRouter()
const authStore = useAuthStore()

async function handleRegister() {
  loading.value = true
  error.value = ''
  try {
    await authStore.register(form)
    router.push({ name: 'tasks' })
  } catch (e: any) {
    const detail = e.response?.data?.detail
    error.value =
      typeof detail === 'string'
        ? detail
        : Array.isArray(detail)
          ? detail.map((d: any) => d.msg).join(', ')
          : 'Registration failed'
  } finally {
    loading.value = false
  }
}
</script>