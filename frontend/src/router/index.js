import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { supabase } from '@/services/supabase'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: () => import('@/views/HomeView.vue'),
    },
    {
      path: '/login',
      name: 'login',
      component: () => import('@/views/LoginView.vue'),
    },
    {
      path: '/register',
      name: 'register',
      component: () => import('@/views/RegisterView.vue'),
    },
    {
      path: '/recipes',
      name: 'recipes',
      component: () => import('@/views/RecipesView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/groups',
      name: 'groups',
      component: () => import('@/views/GroupsView.vue'),
      meta: { requiresAuth: true },
    },
  ],
})

// Navigation guard
router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()
  
  if (to.meta.requiresAuth) {
    const { data: { session } } = await supabase.auth.getSession()
    if (!session) {
      next('/login')
      return
    }
  }
  next()
})

export default router
