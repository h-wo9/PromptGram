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
      <div class="relative mt-6 grid grid-cols-2 rounded-lg bg-white/5 p-1 text-sm font-medium">
        <div
          class="absolute inset-y-1 left-1 w-[calc(50%-0.25rem)] rounded-md bg-accent transition-transform duration-300 ease-out"
          :class="mode === 'signup' ? 'translate-x-full' : ''"
          aria-hidden="true"
        ></div>
        <button
          class="relative z-10 py-1.5 transition-colors duration-300"
          :class="mode === 'login' ? 'text-white' : 'text-gray-400'"
          @click="mode = 'login'"
        >
          로그인
        </button>
        <button
          class="relative z-10 py-1.5 transition-colors duration-300"
          :class="mode === 'signup' ? 'text-white' : 'text-gray-400'"
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
        <transition name="collapse">
          <div v-if="mode === 'signup'" class="collapse-field">
            <input
              v-model="nickname"
              type="text"
              required
              minlength="2"
              maxlength="50"
              placeholder="닉네임 (2자 이상)"
              class="w-full rounded-lg bg-white/5 border border-white/10 px-4 py-3 text-sm focus:border-accent focus:outline-none"
            />
          </div>
        </transition>
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

<style scoped>
/* 닉네임 필드 등장/퇴장 — max-height + opacity collapse */
.collapse-field {
  overflow: hidden;
}
.collapse-enter-active,
.collapse-leave-active {
  transition: max-height 0.3s ease, opacity 0.3s ease, margin-top 0.3s ease;
}
.collapse-enter-from,
.collapse-leave-to {
  max-height: 0;
  opacity: 0;
  margin-top: 0 !important; /* space-y-4의 margin-top(1rem)보다 우선 */
}
.collapse-enter-to,
.collapse-leave-from {
  max-height: 3.5rem;
  opacity: 1;
}
@media (prefers-reduced-motion: reduce) {
  .collapse-enter-active,
  .collapse-leave-active {
    transition: opacity 0.15s ease;
  }
  .collapse-enter-from,
  .collapse-leave-to {
    max-height: 3.5rem;
  }
}
</style>
