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
  computed: {
    user() {
      return JSON.parse(localStorage.getItem('user') || 'null')
    }
  },
  methods: {
    logout() {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      this.$router.push('/login')
    }
  }
}
</script>
