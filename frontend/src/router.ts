import { createRouter, createWebHistory } from 'vue-router'
import App from './App.vue'

const routes = [
  { 
    path: '/',
    component: App 
  },
  { 
    path: '/search',
    name: 'search',
    component: () => import('./views/Search.vue'),
    }
]

const router = createRouter({
  history: createWebHistory(),
  routes: routes
})

export default router