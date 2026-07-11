<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const auth = useAuthStore()

const mode = ref('login')
const email = ref('')
const password = ref('')
const nickname = ref('')
const error = ref('')
const loading = ref(false)

async function submit() {
  error.value = ''
  loading.value = true
  try {
    if (mode.value === 'signup') {
      await auth.signup({
        email: email.value,
        password: password.value,
        nickname: nickname.value,
      })
    } else {
      await auth.login({ email: email.value, password: password.value })
    }
    router.push({ name: 'feed' })
  } catch (e) {
    const detail = e.response?.data?.detail
    error.value =
      typeof detail === 'string'
        ? detail
        : '입력값을 확인해주세요 (비밀번호 8자 이상, 닉네임 2자 이상)'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="min-h-screen flex items-center justify-center px-4">
    <div
      class="w-full max-w-md rounded-2xl border border-white/10 bg-white/5 backdrop-blur-xl p-8 shadow-2xl"
    >
      <router-link to="/" class="block text-center text-2xl font-extrabold tracking-tight">
        Prompt<span class="text-accent">Gram</span>
      </router-link>
      <div class="mt-6 grid grid-cols-2 rounded-lg bg-white/5 p-1 text-sm font-medium">
        <button
          :class="mode === 'login' ? 'bg-accent rounded-md py-1.5' : 'py-1.5 text-gray-400'"
          @click="mode = 'login'"
        >
          로그인
        </button>
        <button
          :class="mode === 'signup' ? 'bg-accent rounded-md py-1.5' : 'py-1.5 text-gray-400'"
          @click="mode = 'signup'"
        >
          회원가입
        </button>
      </div>

      <form class="mt-6 space-y-4" @submit.prevent="submit">
        <input
          v-model="email"
          type="email"
          required
          placeholder="이메일"
          class="w-full rounded-lg bg-white/5 border border-white/10 px-4 py-3 text-sm focus:border-accent focus:outline-none"
        />
        <input
          v-if="mode === 'signup'"
          v-model="nickname"
          type="text"
          required
          minlength="2"
          maxlength="50"
          placeholder="닉네임 (2자 이상)"
          class="w-full rounded-lg bg-white/5 border border-white/10 px-4 py-3 text-sm focus:border-accent focus:outline-none"
        />
        <input
          v-model="password"
          type="password"
          required
          :minlength="mode === 'signup' ? 8 : undefined"
          placeholder="비밀번호 (8자 이상)"
          class="w-full rounded-lg bg-white/5 border border-white/10 px-4 py-3 text-sm focus:border-accent focus:outline-none"
        />
        <p v-if="error" class="text-sm text-red-400">{{ error }}</p>
        <button
          type="submit"
          :disabled="loading"
          class="w-full rounded-lg bg-accent hover:bg-blue-500 transition-colors py-3 font-semibold disabled:opacity-50"
        >
          {{ mode === 'login' ? '로그인' : '가입하고 시작하기' }}
        </button>
      </form>
    </div>
  </div>
</template>
