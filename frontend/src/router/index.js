import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = createRouter({
  history: createWebHistory(),
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

export default router
