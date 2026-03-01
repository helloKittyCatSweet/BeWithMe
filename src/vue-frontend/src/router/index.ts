import { createRouter, createWebHistory } from 'vue-router'

const EmptyView = { template: '<div />' }

type AppSession = {
  isLoggedIn?: boolean
  isAdmin?: boolean
  userId?: number
  walletAddress?: string | null
}

const SESSION_KEY = 'app_session'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { path: '/', redirect: '/verification' },
    { path: '/login', name: 'login', component: EmptyView },
    { path: '/verification', name: 'verification', component: EmptyView },
    { path: '/voice-clone', name: 'voice-clone', component: EmptyView },
    { path: '/create-agent', name: 'create-agent', component: EmptyView },
    { path: '/phone-call', name: 'phone-call', component: EmptyView },
    { path: '/user-profile', name: 'user-profile', component: EmptyView },
    { path: '/trust-security', name: 'trust-security', component: EmptyView },
    { path: '/admin-review', name: 'admin-review', component: EmptyView },
    { path: '/:pathMatch(.*)*', redirect: '/verification' },
  ],
})

router.beforeEach((to) => {
  const token = localStorage.getItem('auth_token')
  const rawSession = localStorage.getItem(SESSION_KEY)

  let session: AppSession | null = null
  if (rawSession) {
    try {
      session = JSON.parse(rawSession) as AppSession
    } catch {
      session = null
    }
  }

  const isAuthenticated = !!token || !!session?.isLoggedIn
  const isAdmin = !!session?.isAdmin

  if (to.path !== '/login' && !isAuthenticated) {
    return { path: '/login', query: { redirect: to.fullPath } }
  }

  if (to.path === '/admin-review' && !isAdmin) {
    return { path: '/verification' }
  }

  if (to.path === '/login' && isAuthenticated) {
    const redirect = typeof to.query.redirect === 'string' ? to.query.redirect : '/verification'
    return { path: redirect }
  }

  return true
})

export default router
