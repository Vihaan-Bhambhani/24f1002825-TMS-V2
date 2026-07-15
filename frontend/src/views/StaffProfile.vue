<template>
  <div class="container mt-4">
    <h2>My Profile</h2>

    <!-- Messages -->
    <div v-if="successMsg" class="alert alert-success alert-dismissible fade show mt-3">
      {{ successMsg }}
      <button type="button" class="btn-close" @click="successMsg = ''"></button>
    </div>
    <div v-if="errorMsg" class="alert alert-danger alert-dismissible fade show mt-3">
      {{ errorMsg }}
      <button type="button" class="btn-close" @click="errorMsg = ''"></button>
    </div>

    <div class="card mt-3">
      <div class="card-body">
        <form @submit.prevent="updateProfile">
          <div class="row">
            <div class="col-md-6 mb-3">
              <label class="form-label">Name</label>
              <input type="text" class="form-control" v-model="profile.name" required>
            </div>
            <div class="col-md-6 mb-3">
              <label class="form-label">Email</label>
              <input type="email" class="form-control" :value="profile.email" disabled>
              <small class="text-muted">Email cannot be changed</small>
            </div>
            <div class="col-md-6 mb-3">
              <label class="form-label">Phone</label>
              <input type="text" class="form-control" v-model="profile.phone" placeholder="Enter phone number">
            </div>
            <div class="col-md-6 mb-3">
              <label class="form-label">Member Since</label>
              <input type="text" class="form-control" :value="profile.created_at ? new Date(profile.created_at).toLocaleDateString() : ''" disabled>
            </div>
            <div class="col-md-6 mb-3">
              <label class="form-label">New Password (leave blank to keep current)</label>
              <input type="password" class="form-control" v-model="newPassword" placeholder="Enter new password" minlength="4">
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
  name: 'StaffProfile',
  data() {
    return {
      profile: { name: '', email: '', phone: '', created_at: '' },
      newPassword: '',
      successMsg: '',
      errorMsg: ''
    }
  },
  async created() {
    await this.loadProfile()
  },
  methods: {
    async loadProfile() {
      try {
        const res = await api.get('/api/staff/profile')
        this.profile = res.data
      } catch (err) {
        this.errorMsg = 'Failed to load profile'
      }
    },
    async updateProfile() {
      this.successMsg = ''
      this.errorMsg = ''
      try {
        const payload = { name: this.profile.name, phone: this.profile.phone }
        if (this.newPassword) payload.password = this.newPassword

        const res = await api.put('/api/staff/profile', payload)
        this.successMsg = 'Profile updated successfully!'
        this.newPassword = ''

        // Update localStorage so navbar reflects new name
        localStorage.setItem('user', JSON.stringify(res.data.user))
        window.dispatchEvent(new Event('auth-changed'))
      } catch (err) {
        this.errorMsg = err.response?.data?.error || 'Profile update failed'
      }
    }
  }
}
</script>
