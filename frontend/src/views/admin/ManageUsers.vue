<template>
  <div class="container mt-4">
    <h2>Manage Users</h2>

    <div class="table-responsive mt-3">
      <table class="table table-bordered table-hover">
        <thead class="table-dark">
          <tr>
            <th>ID</th>
            <th>Name</th>
            <th>Email</th>
            <th>Status</th>
            <th>Registered</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="u in users" :key="u.id">
            <td>{{ u.id }}</td>
            <td>{{ u.name }}</td>
            <td>{{ u.email }}</td>
            <td>
              <span class="badge" :class="u.is_blacklisted ? 'bg-danger' : 'bg-success'">
                {{ u.is_blacklisted ? 'Blacklisted' : 'Active' }}
              </span>
            </td>
            <td>{{ new Date(u.created_at).toLocaleDateString() }}</td>
            <td>
              <button class="btn btn-sm" :class="u.is_blacklisted ? 'btn-success' : 'btn-danger'" @click="toggleBlacklist(u.id)">
                {{ u.is_blacklisted ? 'Unblock' : 'Blacklist' }}
              </button>
            </td>
          </tr>
          <tr v-if="users.length === 0">
            <td colspan="6" class="text-center text-muted">No users registered yet</td>
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
  name: 'ManageUsers',
  data() {
    return { users: [] }
  },
  async created() {
    const res = await api.get('/api/admin/users')
    this.users = res.data
  },
  methods: {
    async toggleBlacklist(id) {
      await api.put(`/api/admin/users/${id}/blacklist`)
      const res = await api.get('/api/admin/users')
      this.users = res.data
    }
  }
}
</script>
