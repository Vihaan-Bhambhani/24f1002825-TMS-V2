<template>
  <div class="container mt-4">
    <h2>Search</h2>

    <div class="input-group mb-4">
      <input type="text" class="form-control" placeholder="Search treks, staff, or users..." v-model="query" @keyup.enter="search">
      <button class="btn btn-primary" @click="search">Search</button>
    </div>

    <!-- Trek Results -->
    <div v-if="results.treks.length > 0" class="mb-4">
      <h5>Treks ({{ results.treks.length }})</h5>
      <table class="table table-bordered">
        <thead class="table-light">
          <tr><th>ID</th><th>Name</th><th>Location</th><th>Status</th></tr>
        </thead>
        <tbody>
          <tr v-for="t in results.treks" :key="t.id">
            <td>{{ t.id }}</td><td>{{ t.name }}</td><td>{{ t.location }}</td><td>{{ t.status }}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Staff Results -->
    <div v-if="results.staff.length > 0" class="mb-4">
      <h5>Staff ({{ results.staff.length }})</h5>
      <table class="table table-bordered">
        <thead class="table-light">
          <tr><th>ID</th><th>Name</th><th>Email</th><th>Status</th></tr>
        </thead>
        <tbody>
          <tr v-for="s in results.staff" :key="s.id">
            <td>{{ s.id }}</td><td>{{ s.name }}</td><td>{{ s.email }}</td>
            <td>{{ s.is_blacklisted ? 'Blacklisted' : 'Active' }}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- User Results -->
    <div v-if="results.users.length > 0" class="mb-4">
      <h5>Users ({{ results.users.length }})</h5>
      <table class="table table-bordered">
        <thead class="table-light">
          <tr><th>ID</th><th>Name</th><th>Email</th><th>Status</th></tr>
        </thead>
        <tbody>
          <tr v-for="u in results.users" :key="u.id">
            <td>{{ u.id }}</td><td>{{ u.name }}</td><td>{{ u.email }}</td>
            <td>{{ u.is_blacklisted ? 'Blacklisted' : 'Active' }}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <p v-if="searched && results.treks.length === 0 && results.staff.length === 0 && results.users.length === 0" class="text-muted">
      No results found for "{{ query }}"
    </p>

    <router-link to="/admin" class="btn btn-outline-secondary mt-3">← Back to Dashboard</router-link>
  </div>
</template>

<script>
import api from '../../services/api.js'

export default {
  name: 'SearchView',
  data() {
    return {
      query: '',
      searched: false,
      results: { treks: [], staff: [], users: [] }
    }
  },
  methods: {
    async search() {
      if (!this.query.trim()) return
      const res = await api.get('/api/admin/search', { params: { q: this.query } })
      this.results = res.data
      this.searched = true
    }
  }
}
</script>
