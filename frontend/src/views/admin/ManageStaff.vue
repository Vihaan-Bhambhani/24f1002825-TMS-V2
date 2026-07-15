<template>
  <div class="container mt-4">
    <div class="d-flex justify-content-between align-items-center mb-3">
      <h2>Manage Staff</h2>
      <button class="btn btn-success" @click="showForm = !showForm">
        {{ showForm ? 'Cancel' : '+ Add Staff' }}
      </button>
    </div>

    <!-- Create Staff Form -->
    <div v-if="showForm" class="card mb-4">
      <div class="card-body">
        <h5>Add New Staff Member</h5>
        <div v-if="formError" class="alert alert-danger">{{ formError }}</div>
        <div v-if="formSuccess" class="alert alert-success">{{ formSuccess }}</div>
        <form @submit.prevent="createStaff">
          <div class="row">
            <div class="col-md-6 mb-3">
              <label class="form-label">Name</label>
              <input type="text" class="form-control" v-model="form.name" required>
            </div>
            <div class="col-md-6 mb-3">
              <label class="form-label">Email</label>
              <input type="email" class="form-control" v-model="form.email" required>
            </div>
            <div class="col-md-6 mb-3">
              <label class="form-label">Password</label>
              <input type="password" class="form-control" v-model="form.password" required>
            </div>
            <div class="col-md-6 mb-3">
              <label class="form-label">Confirm Password</label>
              <input type="password" class="form-control" v-model="form.confirm_password" required>
            </div>
          </div>
          <button type="submit" class="btn btn-primary">Create Staff</button>
        </form>
      </div>
    </div>

    <!-- Staff Table -->
    <div class="table-responsive">
      <table class="table table-bordered table-hover">
        <thead class="table-dark">
          <tr>
            <th>ID</th>
            <th>Name</th>
            <th>Email</th>
            <th>Status</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="s in staff" :key="s.id">
            <td>{{ s.id }}</td>
            <td>{{ s.name }}</td>
            <td>{{ s.email }}</td>
            <td>
              <span class="badge" :class="s.is_blacklisted ? 'bg-danger' : 'bg-success'">
                {{ s.is_blacklisted ? 'Blacklisted' : 'Active' }}
              </span>
            </td>
            <td>
              <button class="btn btn-sm" :class="s.is_blacklisted ? 'btn-success' : 'btn-danger'" @click="toggleBlacklist(s.id)">
                {{ s.is_blacklisted ? 'Unblock' : 'Blacklist' }}
              </button>
            </td>
          </tr>
          <tr v-if="staff.length === 0">
            <td colspan="5" class="text-center text-muted">No staff members yet</td>
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
  name: 'ManageStaff',
  data() {
    return {
      staff: [],
      showForm: false,
      formError: '',
      formSuccess: '',
      form: { name: '', email: '', password: '', confirm_password: '' }
    }
  },
  async created() {
    await this.loadStaff()
  },
  methods: {
    async loadStaff() {
      const res = await api.get('/api/admin/staff')
      this.staff = res.data
    },
    async createStaff() {
      this.formError = ''
      this.formSuccess = ''
      if (this.form.password !== this.form.confirm_password) {
        this.formError = 'Passwords do not match'
        return
      }
      try {
        await api.post('/api/admin/staff', this.form)
        this.formSuccess = 'Staff member created!'
        this.form = { name: '', email: '', password: '', confirm_password: '' }
        await this.loadStaff()
      } catch (err) {
        this.formError = err.response?.data?.error || 'Failed to create staff'
      }
    },
    async toggleBlacklist(id) {
      await api.put(`/api/admin/users/${id}/blacklist`)
      await this.loadStaff()
    }
  }
}
</script>
