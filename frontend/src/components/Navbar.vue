<template>
  <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
    <div class="container">
      <router-link class="navbar-brand" to="/">TMS V2</router-link>

      <div class="navbar-nav ms-auto">
        <template v-if="user">
          <span class="navbar-text me-3">
            {{ user.name }} ({{ user.role }})
          </span>
          <button class="btn btn-outline-light btn-sm" @click="logout">Logout</button>
        </template>
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
