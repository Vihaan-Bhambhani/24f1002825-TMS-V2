<template>
  <div class="container mt-4">
    <h2>My Bookings</h2>

    <!-- Messages -->
    <div v-if="successMsg" class="alert alert-success alert-dismissible fade show mt-3">
      {{ successMsg }}
      <button type="button" class="btn-close" @click="successMsg = ''"></button>
    </div>
    <div v-if="errorMsg" class="alert alert-danger alert-dismissible fade show mt-3">
      {{ errorMsg }}
      <button type="button" class="btn-close" @click="errorMsg = ''"></button>
    </div>

    <!-- Bookings Table -->
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
    <div class="mt-3">
      <button class="btn btn-outline-secondary" @click="exportBookings" :disabled="exporting">
        {{ exporting ? 'Exporting...' : '📥 Export My Booking History (CSV)' }}
      </button>
    </div>
  </div>
</template>

<script>
import api from '../services/api.js'

export default {
  name: 'UserBookings',
  data() {
    return {
      bookings: [],
      successMsg: '',
      errorMsg: '',
      exporting: false
    }
  },
  async created() {
    await this.loadBookings()
  },
  methods: {
    async loadBookings() {
      const res = await api.get('/api/bookings')
      this.bookings = res.data
    },
    showMessage(type, msg) {
      this.successMsg = ''
      this.errorMsg = ''
      if (type === 'success') this.successMsg = msg
      else this.errorMsg = msg
      setTimeout(() => { this.successMsg = ''; this.errorMsg = '' }, 4000)
    },
    async cancelBooking(bookingId) {
      try {
        await api.put(`/api/bookings/${bookingId}/cancel`)
        this.showMessage('success', 'Booking cancelled')
        await this.loadBookings()
      } catch (err) {
        this.showMessage('error', err.response?.data?.error || 'Cancellation failed')
      }
    },
    async exportBookings() {
      this.exporting = true
      try {
        const res = await api.post('/api/export/bookings')
        const taskId = res.data.task_id
        this.showMessage('success', 'Export started! Processing...')

        const filename = await this.pollExportStatus(taskId)

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
        this.showMessage('error', err.response?.data?.error || err.message || 'Export failed. Is the Celery worker running?')
      } finally {
        this.exporting = false
      }
    },
    pollExportStatus(taskId) {
      return new Promise((resolve, reject) => {
        const interval = setInterval(async () => {
          try {
            const res = await api.get(`/api/export/status/${taskId}`)
            if (res.data.status === 'done') {
              clearInterval(interval)
              resolve(res.data.filename)
            } else if (res.data.status === 'failed') {
              clearInterval(interval)
              reject(new Error(res.data.error || 'Export failed'))
            }
          } catch (err) {
            clearInterval(interval)
            reject(err)
          }
        }, 2000)
      })
    }
  }
}
</script>
