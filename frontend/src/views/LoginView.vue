<template>
  <div class="container mt-5">
    <div class="row justify-content-center">
      <div class="col-md-5">
        <div class="card shadow-sm">
          <div class="card-body p-4">
            <h3 class="text-center mb-4">Login</h3>

            <div v-if="error" class="alert alert-danger">{{ error }}</div>

            <form @submit.prevent="login">
              <div class="mb-3">
                <label class="form-label">Email</label>
                <input type="email" class="form-control" v-model="email" required>
              </div>
              <div class="mb-3">
                <label class="form-label">Password</label>
                <input type="password" class="form-control" v-model="password" required>
              </div>
              <button type="submit" class="btn btn-primary w-100" :disabled="loading">
                {{ loading ? 'Logging in...' : 'Login' }}
              </button>
            </form>

            <p class="text-center mt-3">
              Don't have an account?
              <router-link to="/register">Register here</router-link>
            </p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import api from '../services/api.js'

export default {
  name: 'LoginView',
  data() {
    return {
      email: '',
      password: '',
      error: '',
      loading: false
    }
  },
  methods: {
    async login() {
      this.error = ''
      this.loading = true

      try {
        const response = await api.post('/api/login', {
          email: this.email,
          password: this.password
        })

        // Store token and user info
        localStorage.setItem('token', response.data.token)
        localStorage.setItem('user', JSON.stringify(response.data.user))
        window.dispatchEvent(new Event('auth-changed'))

        // Redirect based on role
        const role = response.data.user.role
        if (role === 'admin') this.$router.push('/admin')
        else if (role === 'staff') this.$router.push('/staff')
        else this.$router.push('/dashboard')

      } catch (err) {
        this.error = err.response?.data?.error || 'Login failed'
      } finally {
        this.loading = false
      }
    }
  }
}
</script>
