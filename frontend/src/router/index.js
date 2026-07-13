import { createRouter, createWebHistory } from 'vue-router'
import { suspendLightTheme } from '../composables/theme'
import { useAuthStore } from '../stores/auth'

const TITLES = {
  landing: null,
  auth: '시작하기',
  feed: '피드',
  write: '새 프롬프트',
  edit: '프롬프트 수정',
  mypage: '마이페이지',
}

const router = createRouter({
  history: createWebHistory(),
  // 뒤로가기는 이전 스크롤 위치 복원 (zoom 전환이 끝난 뒤), 그 외엔 맨 위로
  scrollBehavior(to, from, savedPosition) {
    return new Promise((resolve) => {
      setTimeout(() => resolve(savedPosition ?? { top: 0 }), savedPosition ? 480 : 0)
    })
  },
  routes: [
    {
      path: '/',
      name: 'landing',
      component: () => import('../views/LandingView.vue'),
      meta: { guestOnly: true },
    },
    {
      path: '/auth',
      name: 'auth',
      component: () => import('../views/AuthView.vue'),
      meta: { guestOnly: true },
    },
    {
      path: '/feed',
      name: 'feed',
      component: () => import('../views/FeedView.vue'),
    },
    {
      path: '/write',
      name: 'write',
      component: () => import('../views/PromptEditView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/write/:id',
      name: 'edit',
      component: () => import('../views/PromptEditView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/me',
      name: 'mypage',
      component: () => import('../views/MyPageView.vue'),
      meta: { requiresAuth: true },
    },
  ],
})

router.beforeEach(async (to) => {
  const auth = useAuthStore()
  await auth.ensureSession()
  if (to.meta.requiresAuth && !auth.isLoggedIn) return { name: 'auth' }
  if (to.meta.guestOnly && auth.isLoggedIn) return { name: 'feed' }
})

router.afterEach((to) => {
  const title = TITLES[to.name]
  document.title = title ? `${title} · PromptGram` : 'PromptGram'
  // 랜딩·로그인은 항상 다크 (라이트 설정은 유지하되 해당 페이지에서만 해제)
  suspendLightTheme(to.name === 'landing' || to.name === 'auth')
})

export default router
