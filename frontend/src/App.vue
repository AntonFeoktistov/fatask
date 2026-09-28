<script setup lang="ts">
import { watch } from 'vue'
import { useRouter } from 'vue-router'
import { RouterView } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()
const router = useRouter()

watch(
  () => authStore.isAuthenticated,
  (isAuth) => {
    if (!isAuth && router.currentRoute.value.meta.requiresAuth) {
      router.push({ name: 'login' })
    }
  }
)
</script>

<template>
  <RouterView />
</template>