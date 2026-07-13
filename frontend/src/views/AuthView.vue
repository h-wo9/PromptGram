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
  <div class="relative min-h-screen flex items-center justify-center px-4 overflow-hidden">
    <!-- 배경: 랜딩과 이어지는 blue↔violet 대기 조명 -->
    <div class="absolute inset-0 pointer-events-none" aria-hidden="true">
      <div class="auth-blob auth-blob--blue"></div>
      <div class="auth-blob auth-blob--violet"></div>
      <div class="auth-grid"></div>
      <div class="auth-vignette absolute inset-0"></div>
    </div>

    <div
      class="relative w-full max-w-md rounded-2xl border border-white/10 bg-white/5 light:border-slate-200 light:bg-white/80 backdrop-blur-xl p-8 shadow-2xl shadow-[0_20px_80px_rgba(40,60,180,0.18)]"
    >
      <router-link to="/" class="block text-center text-2xl font-extrabold tracking-tight">
        Prompt<span class="text-accent">Gram</span>
      </router-link>
      <div class="relative mt-6 grid grid-cols-2 rounded-lg bg-white/5 light:bg-slate-900/[0.06] p-1 text-sm font-medium">
        <div
          class="absolute inset-y-1 left-1 w-[calc(50%-0.25rem)] rounded-md bg-accent transition-transform duration-300 ease-out"
          :class="mode === 'signup' ? 'translate-x-full' : ''"
          aria-hidden="true"
        ></div>
        <button
          class="relative z-10 py-1.5 transition-colors duration-300"
          :class="mode === 'login' ? 'text-white' : 'text-gray-400 light:text-slate-500'"
          @click="mode = 'login'"
        >
          로그인
        </button>
        <button
          class="relative z-10 py-1.5 transition-colors duration-300"
          :class="mode === 'signup' ? 'text-white' : 'text-gray-400 light:text-slate-500'"
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
          class="w-full rounded-lg bg-white/5 border border-white/10 light:bg-white light:border-slate-300 px-4 py-3 text-sm focus:border-accent focus:outline-none"
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
              class="w-full rounded-lg bg-white/5 border border-white/10 light:bg-white light:border-slate-300 px-4 py-3 text-sm focus:border-accent focus:outline-none"
            />
          </div>
        </transition>
        <input
          v-model="password"
          type="password"
          required
          :minlength="mode === 'signup' ? 8 : undefined"
          placeholder="비밀번호 (8자 이상)"
          class="w-full rounded-lg bg-white/5 border border-white/10 light:bg-white light:border-slate-300 px-4 py-3 text-sm focus:border-accent focus:outline-none"
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
.auth-vignette {
  background: radial-gradient(ellipse at center, transparent 35%, #0a0a0a 95%);
}
:global(.light) .auth-vignette {
  background: radial-gradient(ellipse at center, transparent 35%, #f5f7fb 95%);
}
:global(.light) .auth-grid {
  background-image:
    linear-gradient(rgba(15, 23, 42, 0.05) 1px, transparent 1px),
    linear-gradient(90deg, rgba(15, 23, 42, 0.05) 1px, transparent 1px);
}

/* ── 배경 대기 조명: 천천히 떠다니는 blue/violet blob (transform만) ── */
.auth-blob {
  position: absolute;
  width: 55vmax;
  height: 55vmax;
  border-radius: 9999px;
  will-change: transform;
}
.auth-blob--blue {
  top: -22vmax;
  left: -14vmax;
  background: radial-gradient(closest-side, rgba(0, 112, 243, 0.45), rgba(0, 112, 243, 0.14) 50%, transparent 72%);
  animation: blob-float 16s ease-in-out infinite alternate;
}
.auth-blob--violet {
  bottom: -24vmax;
  right: -16vmax;
  background: radial-gradient(closest-side, rgba(124, 58, 237, 0.42), rgba(124, 58, 237, 0.13) 50%, transparent 72%);
  animation: blob-float 19s ease-in-out infinite alternate-reverse;
}
@keyframes blob-float {
  0% { transform: translate(0, 0) scale(1); }
  100% { transform: translate(6vmax, -5vmax) scale(1.12); }
}
/* 은은한 grid — 공간감 */
.auth-grid {
  position: absolute;
  inset: 0;
  background-image:
    linear-gradient(rgba(255, 255, 255, 0.035) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255, 255, 255, 0.035) 1px, transparent 1px);
  background-size: 56px 56px;
  mask-image: radial-gradient(ellipse at center, black 20%, transparent 70%);
  -webkit-mask-image: radial-gradient(ellipse at center, black 20%, transparent 70%);
}
@media (prefers-reduced-motion: reduce) {
  .auth-blob--blue,
  .auth-blob--violet {
    animation: none;
  }
}

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
