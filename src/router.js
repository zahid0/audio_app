import { createWebHashHistory, createRouter } from 'vue-router'
import Home from './views/Home.vue'
import Login from './views/Login.vue'
import store from './store/index'

const routes = [
    { path: '/', name: 'Home', component: Home },
    { path: '/login', name: 'Login', component: Login, meta: { guest: true } }
  ]

const router = createRouter({
  history: createWebHashHistory(),
  routes,
})
  
router.beforeEach((to, from, next) => {
  if (to.name !== 'Login' && !store.getters.isAuthenticated) next({ name: 'Login' })
  else next()
})

export default router
