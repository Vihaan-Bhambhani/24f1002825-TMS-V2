<template>
  <div class="container mt-4">
    <h2>User Dashboard</h2>

    <!-- Success/Error Messages -->
    <div v-if="successMsg" class="alert alert-success alert-dismissible fade show mt-3">
      {{ successMsg }}
      <button type="button" class="btn-close" @click="successMsg = ''"></button>
    </div>
    <div v-if="errorMsg" class="alert alert-danger alert-dismissible fade show mt-3">
      {{ errorMsg }}
      <button type="button" class="btn-close" @click="errorMsg = ''"></button>
    </div>

    <!-- Browse Treks -->
    <h4 class="mt-4">Available Treks</h4>

    <!-- Search & Filter Bar -->
    <div class="row mt-2 mb-3">
      <div class="col-md-4 mb-2">
        <input type="text" class="form-control" placeholder="Search by name or location..." v-model="searchQuery" @keyup.enter="loadTreks">
      </div>
      <div class="col-md-2 mb-2">
        <select class="form-select" v-model="filterDifficulty" @change="loadTreks">
          <option value="">All Difficulties</option>
          <option value="easy">Easy</option>
          <option value="moderate">Moderate</option>
          <option value="hard">Hard</option>
        </select>
      </div>
      <div class="col-md-2 mb-2">
        <input type="number" class="form-control" placeholder="Max days" v-model="filterDuration" min="1" @change="loadTreks">
      </div>
      <div class="col-md-2 mb-2">
        <button class="btn btn-primary w-100" @click="loadTreks">Search</button>
      </div>
      <div class="col-md-2 mb-2">
        <button class="btn btn-outline-secondary w-100" @click="clearFilters">Clear</button>
      </div>
    </div>

    <div v-if="treks.length === 0" class="text-muted mt-2">No treks match your filters.</div>
    <div class="row mt-3">
      <div class="col-md-4 mb-3" v-for="trek in treks" :key="trek.id">
        <div class="card h-100">
          <div class="card-body">
            <h5 class="card-title">{{ trek.name }}</h5>
            <p class="card-text text-muted">{{ trek.location }}</p>
            <ul class="list-unstyled small">
              <li><strong>Difficulty:</strong> {{ trek.difficulty }}</li>
              <li><strong>Duration:</strong> {{ trek.duration }} days</li>
              <li><strong>Slots:</strong> {{ trek.available_slots }}</li>
              <li v-if="trek.start_date"><strong>Dates:</strong> {{ trek.start_date }} to {{ trek.end_date }}</li>
            </ul>
            <p class="small" v-if="trek.description">{{ trek.description }}</p>
          </div>
          <div class="card-footer">
            <button class="btn btn-success w-100" @click="bookTrek(trek.id)" :disabled="trek.available_slots <= 0">
              {{ trek.available_slots > 0 ? 'Book Now' : 'Full' }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- My Bookings -->
    <h4 class="mt-5">My Bookings</h4>
    <div class="table-responsive mt-3">
      <table class="table table-bordered table-hover">
        <thead class="table-dark">
          <tr>
            <th>Trek</th>
            <th>Location</th>
            <th>Trek Dates</th>
            <th>Booking Date</th>
            <th>Status</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="b in bookings" :key="b.id">
            <td>{{ b.trek_name }}</td>
            <td>{{ b.trek_location }}</td>
            <td>{{ b.trek_start_date || '-' }} to {{ b.trek_end_date || '-' }}</td>
            <td>{{ new Date(b.booking_date).toLocaleDateString() }}</td>
            <td>
              <span class="badge" :class="b.booking_status === 'booked' ? 'bg-primary' : b.booking_status === 'cancelled' ? 'bg-danger' : 'bg-success'">
                {{ b.booking_status }}
              </span>
            </td>
            <td>
              <button v-if="b.booking_status === 'booked'" class="btn btn-sm btn-danger" @click="cancelBooking(b.id)">
                Cancel
              </button>
              <span v-else class="text-muted">—</span>
            </td>
          </tr>
          <tr v-if="bookings.length === 0">
            <td colspan="6" class="text-center text-muted">No bookings yet</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Export Booking History -->
    <div class="mt-3 mb-4">
      <button class="btn btn-outline-secondary" @click="exportBookings" :disabled="exporting">
        {{ exporting ? 'Exporting...' : '📥 Export My Booking History (CSV)' }}
      </button>
    </div>

    <!-- Profile Section -->
    <hr>
    <h4>My Profile</h4>
    <div class="card mt-3 mb-4">
      <div class="card-body">
        <form @submit.prevent="updateProfile">
          <div class="row">
            <div class="col-md-6 mb-3">
              <label class="form-label">Name</label>
              <input type="text" class="form-control" v-model="profile.name">
            </div>
            <div class="col-md-6 mb-3">
              <label class="form-label">Email</label>
              <input type="email" class="form-control" :value="profile.email" disabled>
              <small class="text-muted">Email cannot be changed</small>
            </div>
            <div class="col-md-6 mb-3">
              <label class="form-label">New Password (leave blank to keep current)</label>
              <input type="password" class="form-control" v-model="newPassword" placeholder="Enter new password">
            </div>
          </div>
          <button type="submit" class="btn btn-primary">Update Profile</button>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import api from '../services/api.js'

export default {
  name: 'UserDashboard',
  data() {
    return {
      treks: [],
      bookings: [],
      successMsg: '',
      errorMsg: '',
      searchQuery: '',
      filterDifficulty: '',
      filterDuration: '',
      exporting: false,
      profile: { name: '', email: '' },
      newPassword: ''
    }
  },
  async created() {
    await this.loadData()
    await this.loadProfile()
  },
  methods: {
    async loadData() {
      await Promise.all([this.loadTreks(), this.loadBookings()])
    },
    async loadTreks() {
      const params = {}
      if (this.searchQuery) params.search = this.searchQuery
      if (this.filterDifficulty) params.difficulty = this.filterDifficulty
      if (this.filterDuration) params.duration = this.filterDuration
      const res = await api.get('/api/treks', { params })
      this.treks = res.data
    },
    async loadBookings() {
      const res = await api.get('/api/bookings')
      this.bookings = res.data
    },
    async loadProfile() {
      try {
        const res = await api.get('/api/profile')
        this.profile = res.data
      } catch (err) {
        console.error('Failed to load profile:', err)
      }
    },
    clearFilters() {
      this.searchQuery = ''
      this.filterDifficulty = ''
      this.filterDuration = ''
      this.loadTreks()
    },
    showMessage(type, msg) {
      this.successMsg = ''
      this.errorMsg = ''
      if (type === 'success') this.successMsg = msg
      else this.errorMsg = msg
      setTimeout(() => { this.successMsg = ''; this.errorMsg = '' }, 4000)
    },
    async bookTrek(trekId) {
      try {
        await api.post('/api/bookings', { trek_id: trekId })
        this.showMessage('success', 'Trek booked successfully!')
        await this.loadData()
      } catch (err) {
        this.showMessage('error', err.response?.data?.error || 'Booking failed')
      }
    },
    async cancelBooking(bookingId) {
      try {
        await api.put(`/api/bookings/${bookingId}/cancel`)
        this.showMessage('success', 'Booking cancelled')
        await this.loadData()
      } catch (err) {
        this.showMessage('error', err.response?.data?.error || 'Cancellation failed')
      }
    },
    async exportBookings() {
      this.exporting = true
      try {
        const res = await api.post('/api/export/bookings')
        const filename = res.data.filename

        const downloadRes = await api.get(`/api/download/${filename}`, { responseType: 'blob' })
        const url = window.URL.createObjectURL(new Blob([downloadRes.data]))
        const link = document.createElement('a')
        link.href = url
        link.download = filename
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
        window.URL.revokeObjectURL(url)

        this.showMessage('success', 'Booking history exported!')
      } catch (err) {
        this.showMessage('error', err.response?.data?.error || 'Export failed. Is the Celery worker running?')
      } finally {
        this.exporting = false
      }
    },
    async updateProfile() {
      try {
        const payload = { name: this.profile.name }
        if (this.newPassword) payload.password = this.newPassword

        const res = await api.put('/api/profile', payload)
        this.showMessage('success', 'Profile updated!')
        this.newPassword = ''

        // Update localStorage so navbar reflects new name
        localStorage.setItem('user', JSON.stringify(res.data.user))
      } catch (err) {
        this.showMessage('error', err.response?.data?.error || 'Profile update failed')
      }
    }
  }
}
</script>
