<template>
  <div class="container mt-4">
    <h2>All Bookings</h2>

    <div class="table-responsive mt-3">
      <table class="table table-bordered table-hover">
        <thead class="table-dark">
          <tr>
            <th>ID</th>
            <th>User</th>
            <th>Email</th>
            <th>Trek</th>
            <th>Booking Date</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="b in bookings" :key="b.id">
            <td>{{ b.id }}</td>
            <td>{{ b.user_name }}</td>
            <td>{{ b.user_email }}</td>
            <td>{{ b.trek_name }}</td>
            <td>{{ new Date(b.booking_date).toLocaleDateString() }}</td>
            <td>
              <span class="badge" :class="bookingBadge(b.booking_status)">{{ b.booking_status }}</span>
            </td>
          </tr>
          <tr v-if="bookings.length === 0">
            <td colspan="6" class="text-center text-muted">No bookings yet</td>
          </tr>
        </tbody>
      </table>
    </div>

    <router-link to="/admin" class="btn btn-outline-secondary mt-3">← Back to Dashboard</router-link>
  </div>
</template>

<script>
import api from '../../services/api.js'

export default {
  name: 'ManageBookings',
  data() {
    return { bookings: [] }
  },
  async created() {
    const res = await api.get('/api/admin/bookings')
    this.bookings = res.data
  },
  methods: {
    bookingBadge(status) {
      const map = { booked: 'bg-primary', cancelled: 'bg-danger', completed: 'bg-success' }
      return map[status] || 'bg-secondary'
    }
  }
}
</script>
