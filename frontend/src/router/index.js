import { createRouter, createWebHistory } from 'vue-router'

import LoginView from '../views/LoginView.vue'
import RegisterView from '../views/RegisterView.vue'
import AdminDashboard from '../views/AdminDashboard.vue'
import StaffDashboard from '../views/StaffDashboard.vue'
import StaffProfile from '../views/StaffProfile.vue'
import UserDashboard from '../views/UserDashboard.vue'
import UserBookings from '../views/UserBookings.vue'
import UserProfile from '../views/UserProfile.vue'

// Admin sub-pages
import ManageTreks from '../views/admin/ManageTreks.vue'
import ManageStaff from '../views/admin/ManageStaff.vue'
import ManageUsers from '../views/admin/ManageUsers.vue'
import ManageBookings from '../views/admin/ManageBookings.vue'
import SearchView from '../views/admin/SearchView.vue'

const routes = [
  { path: '/', redirect: '/login' },
  { path: '/login', name: 'Login', component: LoginView, meta: { guest: true } },
  { path: '/register', name: 'Register', component: RegisterView, meta: { guest: true } },

  // Admin routes
  { path: '/admin', name: 'AdminDashboard', component: AdminDashboard, meta: { requiresAuth: true, role: 'admin' } },
  { path: '/admin/treks', name: 'ManageTreks', component: ManageTreks, meta: { requiresAuth: true, role: 'admin' } },
  { path: '/admin/staff', name: 'ManageStaff', component: ManageStaff, meta: { requiresAuth: true, role: 'admin' } },
  { path: '/admin/users', name: 'ManageUsers', component: ManageUsers, meta: { requiresAuth: true, role: 'admin' } },
  { path: '/admin/bookings', name: 'ManageBookings', component: ManageBookings, meta: { requiresAuth: true, role: 'admin' } },
  { path: '/admin/search', name: 'AdminSearch', component: SearchView, meta: { requiresAuth: true, role: 'admin' } },

  // Staff and User routes
  { path: '/staff', name: 'StaffDashboard', component: StaffDashboard, meta: { requiresAuth: true, role: 'staff' } },
  { path: '/staff/profile', name: 'StaffProfile', component: StaffProfile, meta: { requiresAuth: true, role: 'staff' } },
  { path: '/dashboard', name: 'UserDashboard', component: UserDashboard, meta: { requiresAuth: true, role: 'trekker' } },
  { path: '/bookings', name: 'UserBookings', component: UserBookings, meta: { requiresAuth: true, role: 'trekker' } },
  { path: '/profile', name: 'UserProfile', component: UserProfile, meta: { requiresAuth: true, role: 'trekker' } }
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
    if (user.role === 'admin') return next('/admin')
    if (user.role === 'staff') return next('/staff')
    return next('/dashboard')
  }

  next()
})

export default router
