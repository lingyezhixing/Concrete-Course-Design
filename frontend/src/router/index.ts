import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'
import AppLayout from '../components/layout/AppLayout.vue'
import { useAuth } from '../composables/useAuth'

const routes: RouteRecordRaw[] = [
  {
    path: '/login',
    name: 'login',
    component: () => import('../views/Login.vue'),
    meta: { public: true },
  },
  {
    path: '/',
    component: AppLayout,
    children: [
      { path: '', name: 'overview', component: () => import('../views/Overview.vue') },
      { path: 'params', name: 'params', component: () => import('../views/Params.vue') },
      { path: 'slab', name: 'slab', component: () => import('../views/Slab.vue') },
      { path: 'beam', name: 'beam', component: () => import('../views/SecondaryBeam.vue') },
      { path: 'main_beam', name: 'main_beam', component: () => import('../views/MainBeam.vue') },
      { path: 'report', name: 'report', component: () => import('../views/Report.vue') },
      { path: 'archive', name: 'archive', component: () => import('../views/Archive.vue') },
      { path: 'settings', name: 'settings', component: () => import('../views/Settings.vue') },
    ],
  },
  { path: '/:pathMatch(.*)*', redirect: '/' },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to) => {
  const { isAuthenticated } = useAuth()
  if (!to.meta.public && !isAuthenticated.value) {
    return { name: 'login', query: { redirect: to.fullPath } }
  }
  if (to.name === 'login' && isAuthenticated.value) {
    return { path: '/' }
  }
  return true
})

export default router
