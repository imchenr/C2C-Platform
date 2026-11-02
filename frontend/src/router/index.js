import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes = [
  {
    path: '/',
    component: () => import('@/layouts/CLayout.vue'),
    children: [
      { path: '', name: 'home', component: () => import('@/views/HomeView.vue') },
      { path: 'market', name: 'market', component: () => import('@/views/MarketView.vue') },
      { path: 'product/:id', name: 'product-detail', component: () => import('@/views/ProductDetailView.vue') },
      { path: 'publish/:id?', name: 'publish', component: () => import('@/views/PublishView.vue'), meta: { requiresAuth: true } },
      { path: 'favorites', name: 'favorites', component: () => import('@/views/FavoritesView.vue'), meta: { requiresAuth: true } },
      { path: 'messages/:id?', name: 'messages', component: () => import('@/views/MessagesView.vue'), meta: { requiresAuth: true } },
      { path: 'orders', name: 'orders', component: () => import('@/views/OrdersView.vue'), meta: { requiresAuth: true } },
      { path: 'profile', name: 'profile', component: () => import('@/views/ProfileView.vue'), meta: { requiresAuth: true } },
    ],
  },
  { path: '/login', name: 'login', component: () => import('@/views/AuthView.vue'), meta: { guest: true } },
  { path: '/register', name: 'register', component: () => import('@/views/AuthView.vue'), meta: { guest: true } },
  {
    path: '/admin',
    component: () => import('@/layouts/AdminLayout.vue'),
    meta: { requiresAdmin: true },
    children: [
      { path: '', name: 'admin-dashboard', component: () => import('@/views/admin/DashboardView.vue') },
      { path: 'users', name: 'admin-users', component: () => import('@/views/admin/UsersView.vue') },
      { path: 'products', name: 'admin-products', component: () => import('@/views/admin/ProductsView.vue') },
      { path: 'orders', name: 'admin-orders', component: () => import('@/views/admin/OrdersView.vue') },
      { path: 'reports', name: 'admin-reports', component: () => import('@/views/admin/ReportsView.vue') },
      { path: 'operations', name: 'admin-operations', component: () => import('@/views/admin/OperationsView.vue') },
      { path: 'settings', name: 'admin-settings', component: () => import('@/views/admin/SettingsView.vue') },
    ],
  },
  { path: '/:pathMatch(.*)*', redirect: '/' },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior: () => ({ top: 0 }),
})

router.beforeEach((to) => {
  const auth = useAuthStore()
  if (to.meta.requiresAuth && !auth.isLoggedIn) return { name: 'login', query: { redirect: to.fullPath } }
  if (to.matched.some((item) => item.meta.requiresAdmin) && !auth.isAdmin) return { name: 'login', query: { redirect: '/admin' } }
  if (to.meta.guest && auth.isLoggedIn) return auth.isAdmin ? '/admin' : '/'
})

export default router

