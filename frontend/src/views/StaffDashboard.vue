<template>
  <div class="container mt-4">
    <h2>Staff Dashboard</h2>

    <!-- Stats -->
    <div class="row mt-4 mb-4">
      <div class="col-md-6 mb-3">
        <div class="card text-center">
          <div class="card-body">
            <h5 class="card-title text-muted">Assigned Treks</h5>
            <h2>{{ stats.assigned_treks }}</h2>
          </div>
        </div>
      </div>
      <div class="col-md-6 mb-3">
        <div class="card text-center">
          <div class="card-body">
            <h5 class="card-title text-muted">Total Bookings</h5>
            <h2>{{ stats.total_bookings }}</h2>
          </div>
        </div>
      </div>
    </div>

    <!-- Assigned Treks -->
    <h4>My Assigned Treks</h4>
    <div class="table-responsive mt-3">
      <table class="table table-bordered table-hover">
        <thead class="table-dark">
          <tr>
            <th>Name</th>
            <th>Location</th>
            <th>Difficulty</th>
            <th>Slots</th>
            <th>Dates</th>
            <th>Bookings</th>
            <th>Status</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="trek in treks" :key="trek.id">
            <td>{{ trek.name }}</td>
            <td>{{ trek.location }}</td>
            <td>{{ trek.difficulty }}</td>
            <td>
              <div class="d-flex align-items-center">
                <input type="number" class="form-control form-control-sm me-1" style="width: 70px" :value="trek.available_slots" @change="updateSlots(trek.id, $event.target.value)" min="0">
              </div>
            </td>
            <td>{{ trek.start_date || '-' }} to {{ trek.end_date || '-' }}</td>
            <td>{{ trek.booking_count }}</td>
            <td>
              <select class="form-select form-select-sm" :value="trek.status" @change="updateStatus(trek.id, $event.target.value)">
                <option value="pending">Pending</option>
                <option value="approved">Approved</option>
                <option value="open">Open</option>
                <option value="closed">Closed</option>
                <option value="completed">Completed</option>
              </select>
            </td>
            <td>
              <button class="btn btn-sm btn-info" @click="viewBookings(trek)">View Bookings</button>
            </td>
          </tr>
          <tr v-if="treks.length === 0">
            <td colspan="8" class="text-center text-muted">No treks assigned to you yet</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Bookings for selected trek -->
    <div v-if="selectedTrek" class="card mt-4">
      <div class="card-header d-flex justify-content-between">
        <strong>Bookings for "{{ selectedTrek.name }}"</strong>
        <button class="btn btn-sm btn-secondary" @click="selectedTrek = null; trekBookings = []">Close</button>
      </div>
      <div class="card-body">
        <table class="table table-bordered" v-if="trekBookings.length > 0">
          <thead class="table-light">
            <tr>
              <th>User</th>
              <th>Email</th>
              <th>Booking Date</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="b in trekBookings" :key="b.id">
              <td>{{ b.user_name }}</td>
              <td>{{ b.user_email }}</td>
              <td>{{ new Date(b.booking_date).toLocaleDateString() }}</td>
              <td>
                <span class="badge" :class="b.booking_status === 'booked' ? 'bg-primary' : b.booking_status === 'cancelled' ? 'bg-danger' : 'bg-success'">
                  {{ b.booking_status }}
                </span>
              </td>
              <td>
                <button v-if="b.booking_status === 'booked'" class="btn btn-sm btn-danger" @click="cancelBooking(selectedTrek.id, b.id)">
                  Remove
                </button>
                <span v-else class="text-muted">—</span>
              </td>
            </tr>
          </tbody>
        </table>
        <p v-else class="text-muted">No bookings for this trek yet.</p>
      </div>
    </div>
  </div>
</template>

<script>
import api from '../services/api.js'

export default {
  name: 'StaffDashboard',
  data() {
    return {
      stats: { assigned_treks: 0, total_bookings: 0 },
      treks: [],
      selectedTrek: null,
      trekBookings: []
    }
  },
  async created() {
    await this.loadData()
  },
  methods: {
    async loadData() {
      const [statsRes, treksRes] = await Promise.all([
        api.get('/api/staff/dashboard'),
        api.get('/api/staff/treks')
      ])
      this.stats = statsRes.data
      this.treks = treksRes.data
    },
    async updateStatus(trekId, status) {
      try {
        await api.put(`/api/staff/treks/${trekId}/status`, { status })
        await this.loadData()
      } catch (err) {
        alert(err.response?.data?.error || 'Failed to update status')
      }
    },
    async viewBookings(trek) {
      this.selectedTrek = trek
      const res = await api.get(`/api/staff/treks/${trek.id}/bookings`)
      this.trekBookings = res.data
    },
    async updateSlots(trekId, slots) {
      try {
        await api.put(`/api/staff/treks/${trekId}/slots`, { available_slots: parseInt(slots) })
        await this.loadData()
      } catch (err) {
        alert(err.response?.data?.error || 'Failed to update slots')
      }
    },
    async cancelBooking(trekId, bookingId) {
      if (!confirm('Remove this participant from the trek?')) return
      try {
        await api.put(`/api/staff/treks/${trekId}/bookings/${bookingId}/cancel`)
        await this.viewBookings(this.selectedTrek)
        await this.loadData()
      } catch (err) {
        alert(err.response?.data?.error || 'Failed to remove participant')
      }
    }
  }
}
</script>
