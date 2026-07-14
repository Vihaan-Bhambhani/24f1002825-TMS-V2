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
    <div v-if="treks.length === 0" class="text-muted mt-2">No treks are currently open for booking.</div>
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
            <th>Booking Date</th>
            <th>Status</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="b in bookings" :key="b.id">
            <td>{{ b.trek_name }}</td>
            <td>{{ b.trek_location }}</td>
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
            <td colspan="5" class="text-center text-muted">No bookings yet</td>
          </tr>
        </tbody>
      </table>
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
      errorMsg: ''
    }
  },
  async created() {
    await this.loadData()
  },
  methods: {
    async loadData() {
      const [treksRes, bookingsRes] = await Promise.all([
        api.get('/api/treks'),
        api.get('/api/bookings')
      ])
      this.treks = treksRes.data
      this.bookings = bookingsRes.data
    },
    showMessage(type, msg) {
      this.successMsg = ''
      this.errorMsg = ''
      if (type === 'success') this.successMsg = msg
      else this.errorMsg = msg
      setTimeout(() => { this.successMsg = ''; this.errorMsg = '' }, 3000)
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
    }
  }
}
</script>
