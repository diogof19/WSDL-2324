import { createRouter, createWebHistory } from 'vue-router'
import App from './App.vue'

const routes = [
  { 
    path: '/',
    component: App 
  },
  { 
    path: '/search-results/:results',
    name: 'search-results',
    component: () => import('./views/SearchResults.vue'),
    }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router