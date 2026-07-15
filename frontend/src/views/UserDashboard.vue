<template>
  <div class="container mt-4">
    <h2>Available Treks</h2>

    <!-- Success/Error Messages -->
    <div v-if="successMsg" class="alert alert-success alert-dismissible fade show mt-3">
      {{ successMsg }}
      <button type="button" class="btn-close" @click="successMsg = ''"></button>
    </div>
    <div v-if="errorMsg" class="alert alert-danger alert-dismissible fade show mt-3">
      {{ errorMsg }}
      <button type="button" class="btn-close" @click="errorMsg = ''"></button>
    </div>

    <!-- Search & Filter Bar -->
    <div class="row mt-3 mb-3">
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
  </div>
</template>

<script>
import api from '../services/api.js'

export default {
  name: 'UserDashboard',
  data() {
    return {
      treks: [],
      successMsg: '',
      errorMsg: '',
      searchQuery: '',
      filterDifficulty: '',
      filterDuration: ''
    }
  },
  async created() {
    await this.loadTreks()
  },
  methods: {
    async loadTreks() {
      const params = {}
      if (this.searchQuery) params.search = this.searchQuery
      if (this.filterDifficulty) params.difficulty = this.filterDifficulty
      if (this.filterDuration) params.duration = this.filterDuration
      const res = await api.get('/api/treks', { params })
      this.treks = res.data
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
        await this.loadTreks()
      } catch (err) {
        this.showMessage('error', err.response?.data?.error || 'Booking failed')
      }
    }
  }
}
</script>
