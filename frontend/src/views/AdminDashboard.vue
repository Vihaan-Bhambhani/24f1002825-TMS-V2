<template>
  <div class="container mt-4">
    <h2>Admin Dashboard</h2>

    <!-- Stats Cards -->
    <div class="row mt-4">
      <div class="col-md-3 mb-3">
        <div class="card text-center">
          <div class="card-body">
            <h5 class="card-title text-muted">Total Treks</h5>
            <h2>{{ stats.total_treks }}</h2>
          </div>
        </div>
      </div>
      <div class="col-md-3 mb-3">
        <div class="card text-center">
          <div class="card-body">
            <h5 class="card-title text-muted">Total Users</h5>
            <h2>{{ stats.total_users }}</h2>
          </div>
        </div>
      </div>
      <div class="col-md-3 mb-3">
        <div class="card text-center">
          <div class="card-body">
            <h5 class="card-title text-muted">Total Staff</h5>
            <h2>{{ stats.total_staff }}</h2>
          </div>
        </div>
      </div>
      <div class="col-md-3 mb-3">
        <div class="card text-center">
          <div class="card-body">
            <h5 class="card-title text-muted">Total Bookings</h5>
            <h2>{{ stats.total_bookings }}</h2>
          </div>
        </div>
      </div>
    </div>

    <!-- Quick Links -->
    <div class="row mt-3">
      <div class="col-md-3 mb-2">
        <router-link to="/admin/treks" class="btn btn-primary w-100">Manage Treks</router-link>
      </div>
      <div class="col-md-3 mb-2">
        <router-link to="/admin/staff" class="btn btn-primary w-100">Manage Staff</router-link>
      </div>
      <div class="col-md-3 mb-2">
        <router-link to="/admin/users" class="btn btn-primary w-100">Manage Users</router-link>
      </div>
      <div class="col-md-3 mb-2">
        <router-link to="/admin/bookings" class="btn btn-primary w-100">View Bookings</router-link>
      </div>
    </div>
  </div>
</template>

<script>
import api from '../services/api.js'

export default {
  name: 'AdminDashboard',
  data() {
    return {
      stats: { total_treks: 0, total_users: 0, total_staff: 0, total_bookings: 0 }
    }
  },
  async created() {
    try {
      const response = await api.get('/api/admin/stats')
      this.stats = response.data
    } catch (err) {
      console.error('Failed to load stats:', err)
    }
  }
}
</script>
