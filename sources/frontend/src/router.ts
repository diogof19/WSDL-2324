import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  { 
    path: '/',
    name: 'home',
    component: () => import('./views/Search.vue')
  },
  { 
    path: '/search',
    name: 'search',
    component: () => import('./views/Search.vue'),
  },
  {
    path: '/artist/:uris',
    name: 'artist',
    component: () => import('./pages/ArtistPage.vue'),
  },
  {
    path: '/artwork/:uris',
    name: 'artwork',
    component: () => import('./pages/ArtworkPage.vue'),
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes: routes
})

export default router