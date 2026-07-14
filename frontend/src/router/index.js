import { createRouter, createWebHistory } from 'vue-router'

import LoginView from '../views/LoginView.vue'
import RegisterView from '../views/RegisterView.vue'
import AdminDashboard from '../views/AdminDashboard.vue'
import StaffDashboard from '../views/StaffDashboard.vue'
import UserDashboard from '../views/UserDashboard.vue'

const routes = [
  { path: '/', redirect: '/login' },
  { path: '/login', name: 'Login', component: LoginView, meta: { guest: true } },
  { path: '/register', name: 'Register', component: RegisterView, meta: { guest: true } },
  { path: '/admin', name: 'AdminDashboard', component: AdminDashboard, meta: { requiresAuth: true, role: 'admin' } },
  { path: '/staff', name: 'StaffDashboard', component: StaffDashboard, meta: { requiresAuth: true, role: 'staff' } },
  { path: '/dashboard', name: 'UserDashboard', component: UserDashboard, meta: { requiresAuth: true, role: 'trekker' } }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// Navigation guard — check auth and role before each route
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  const user = JSON.parse(localStorage.getItem('user') || 'null')

  // If route requires auth and user is not logged in
  if (to.meta.requiresAuth && !token) {
    return next('/login')
  }

  // If route is for guests only (login/register) and user is logged in
  if (to.meta.guest && token && user) {
    if (user.role === 'admin') return next('/admin')
    if (user.role === 'staff') return next('/staff')
    return next('/dashboard')
  }

  // If route requires a specific role
  if (to.meta.role && user && user.role !== to.meta.role) {
    // Redirect to their own dashboard
    if (user.role === 'admin') return next('/admin')
    if (user.role === 'staff') return next('/staff')
    return next('/dashboard')
  }

  next()
})

export default router
