import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'
import AppLayout from '../components/layout/AppLayout.vue'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    component: AppLayout,
    children: [
      { path: '', name: 'overview', component: () => import('../views/Overview.vue') },
      { path: 'materials', name: 'materials', component: () => import('../views/Materials.vue') },
      { path: 'slab', name: 'slab', component: () => import('../views/Slab.vue') },
      { path: 'secondary-beam', name: 'secondary-beam', component: () => import('../views/SecondaryBeam.vue') },
      { path: 'main-beam', name: 'main-beam', component: () => import('../views/MainBeam.vue') },
      { path: 'column', name: 'column', component: () => import('../views/Column.vue') },
      { path: 'report', name: 'report', component: () => import('../views/Report.vue') },
      { path: 'settings', name: 'settings', component: () => import('../views/Settings.vue') },
    ],
  },
  { path: '/:pathMatch(.*)*', redirect: '/' },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
