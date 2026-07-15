<template>
  <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
    <div class="container">
      <router-link class="navbar-brand" to="/">TMS V2</router-link>

      <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
        <span class="navbar-toggler-icon"></span>
      </button>

      <div class="collapse navbar-collapse" id="navbarNav">
        <!-- Admin nav links -->
        <ul class="navbar-nav me-auto" v-if="user && user.role === 'admin'">
          <li class="nav-item">
            <router-link class="nav-link" to="/admin">Dashboard</router-link>
          </li>
          <li class="nav-item">
            <router-link class="nav-link" to="/admin/treks">Treks</router-link>
          </li>
          <li class="nav-item">
            <router-link class="nav-link" to="/admin/staff">Staff</router-link>
          </li>
          <li class="nav-item">
            <router-link class="nav-link" to="/admin/users">Users</router-link>
          </li>
          <li class="nav-item">
            <router-link class="nav-link" to="/admin/bookings">Bookings</router-link>
          </li>
          <li class="nav-item">
            <router-link class="nav-link" to="/admin/search">Search</router-link>
          </li>
        </ul>

        <!-- Staff nav links -->
        <ul class="navbar-nav me-auto" v-if="user && user.role === 'staff'">
          <li class="nav-item">
            <router-link class="nav-link" to="/staff">My Dashboard</router-link>
          </li>
        </ul>

        <!-- Trekker nav links -->
        <ul class="navbar-nav me-auto" v-if="user && user.role === 'trekker'">
          <li class="nav-item">
            <router-link class="nav-link" to="/dashboard">Treks</router-link>
          </li>
          <li class="nav-item">
            <router-link class="nav-link" to="/bookings">My Bookings</router-link>
          </li>
          <li class="nav-item">
            <router-link class="nav-link" to="/profile">Profile</router-link>
          </li>
        </ul>

        <div class="navbar-nav ms-auto">
          <template v-if="user">
            <span class="navbar-text me-3">
              {{ user.name }} ({{ user.role }})
            </span>
            <button class="btn btn-outline-light btn-sm" @click="logout">Logout</button>
          </template>
        </div>
      </div>
    </div>
  </nav>
</template>

<script>
export default {
  name: 'NavbarComponent',
  data() {
    return {
      user: JSON.parse(localStorage.getItem('user') || 'null')
    }
  },
  mounted() {
    window.addEventListener('auth-changed', this.refreshUser)
  },
  beforeUnmount() {
    window.removeEventListener('auth-changed', this.refreshUser)
  },
  methods: {
    refreshUser() {
      this.user = JSON.parse(localStorage.getItem('user') || 'null')
    },
    logout() {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      window.dispatchEvent(new Event('auth-changed'))
      this.$router.push('/login')
    }
  }
}
</script>
