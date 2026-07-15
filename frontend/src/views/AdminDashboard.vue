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
        <router-link to="/admin/users" class="btn btn-primary w-100">Manage Users</router-link>
      </div>
      <div class="col-md-3 mb-2">
        <router-link to="/admin/staff" class="btn btn-primary w-100">Manage Staff</router-link>
      </div>
      <div class="col-md-3 mb-2">
        <router-link to="/admin/bookings" class="btn btn-primary w-100">View Bookings</router-link>
      </div>
    </div>

    <!-- Export Section -->
    <div class="row mt-3">
      <div class="col-12">
        <h5>Export Data</h5>
        <div v-if="exportMsg" class="alert" :class="exportError ? 'alert-danger' : 'alert-success'">{{ exportMsg }}</div>
      </div>
      <div class="col-md-3 mb-2">
        <button class="btn btn-outline-secondary w-100" @click="triggerExport('treks')">📥 Export Treks CSV</button>
      </div>
      <div class="col-md-3 mb-2">
        <button class="btn btn-outline-secondary w-100" @click="triggerExport('bookings')">📥 Export Bookings CSV</button>
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
      stats: { total_treks: 0, total_users: 0, total_staff: 0, total_bookings: 0 },
      exportMsg: '',
      exportError: false
    }
  },
  async created() {
    try {
      const response = await api.get('/api/admin/stats')
      this.stats = response.data
    } catch (err) {
      console.error('Failed to load stats:', err)
    }
  },
  methods: {
    async triggerExport(type) {
      this.exportMsg = ''
      this.exportError = false
      this.exportMsg = `Exporting ${type}... please wait.`
      try {
        const res = await api.post(`/api/admin/export/${type}`)
        const filename = res.data.filename

        // Download the file using Axios (JWT sent in header automatically)
        const downloadRes = await api.get(`/api/admin/download/${filename}`, { responseType: 'blob' })
        const url = window.URL.createObjectURL(new Blob([downloadRes.data]))
        const link = document.createElement('a')
        link.href = url
        link.download = filename
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
        window.URL.revokeObjectURL(url)

        this.exportMsg = `${type} exported successfully!`
        setTimeout(() => { this.exportMsg = '' }, 5000)
      } catch (err) {
        this.exportError = true
        this.exportMsg = err.response?.data?.error || 'Export failed. Is the Celery worker running?'
      }
    }
  }
}
</script>
