import { createRouter, createWebHistory } from 'vue-router'
import App from './App.vue'
import SearchResults from './views/SearchResults.vue'

const routes = [
  { path: '/', component: App },
  { path: '/search-results/:data', component: SearchResults, name: 'search-results' }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router