<template>
  <div class="container mt-4">
    <div class="d-flex justify-content-between align-items-center mb-3">
      <h2>Manage Treks</h2>
      <button class="btn btn-success" @click="showForm = !showForm">
        {{ showForm ? 'Cancel' : '+ Create Trek' }}
      </button>
    </div>

    <!-- Create/Edit Form -->
    <div v-if="showForm" class="card mb-4">
      <div class="card-body">
        <h5>{{ editingTrek ? 'Edit Trek' : 'Create Trek' }}</h5>
        <div v-if="formError" class="alert alert-danger">{{ formError }}</div>
        <form @submit.prevent="saveTrek">
          <div class="row">
            <div class="col-md-6 mb-3">
              <label class="form-label">Trek Name</label>
              <input type="text" class="form-control" v-model="form.name" required>
            </div>
            <div class="col-md-6 mb-3">
              <label class="form-label">Location</label>
              <input type="text" class="form-control" v-model="form.location" required>
            </div>
            <div class="col-md-4 mb-3">
              <label class="form-label">Difficulty</label>
              <select class="form-select" v-model="form.difficulty" required>
                <option value="easy">Easy</option>
                <option value="moderate">Moderate</option>
                <option value="hard">Hard</option>
              </select>
            </div>
            <div class="col-md-4 mb-3">
              <label class="form-label">Duration (days)</label>
              <input type="number" class="form-control" v-model="form.duration" min="1" required>
            </div>
            <div class="col-md-4 mb-3">
              <label class="form-label">Available Slots</label>
              <input type="number" class="form-control" v-model="form.available_slots" min="1" required>
            </div>
            <div class="col-md-4 mb-3">
              <label class="form-label">Status</label>
              <select class="form-select" v-model="form.status">
                <option value="pending">Pending</option>
                <option value="approved">Approved</option>
                <option value="open">Open</option>
                <option value="closed">Closed</option>
                <option value="completed">Completed</option>
              </select>
            </div>
            <div class="col-md-4 mb-3">
              <label class="form-label">Start Date</label>
              <input type="date" class="form-control" v-model="form.start_date">
            </div>
            <div class="col-md-4 mb-3">
              <label class="form-label">End Date</label>
              <input type="date" class="form-control" v-model="form.end_date">
            </div>
            <div class="col-12 mb-3">
              <label class="form-label">Description</label>
              <textarea class="form-control" v-model="form.description" rows="2"></textarea>
            </div>
          </div>
          <button type="submit" class="btn btn-primary">{{ editingTrek ? 'Update' : 'Create' }}</button>
        </form>
      </div>
    </div>

    <!-- Treks Table -->
    <div class="table-responsive">
      <table class="table table-bordered table-hover">
        <thead class="table-dark">
          <tr>
            <th>ID</th>
            <th>Name</th>
            <th>Location</th>
            <th>Difficulty</th>
            <th>Slots</th>
            <th>Status</th>
            <th>Staff</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="trek in treks" :key="trek.id">
            <td>{{ trek.id }}</td>
            <td>{{ trek.name }}</td>
            <td>{{ trek.location }}</td>
            <td>{{ trek.difficulty }}</td>
            <td>{{ trek.available_slots }}</td>
            <td><span class="badge" :class="statusBadge(trek.status)">{{ trek.status }}</span></td>
            <td>{{ trek.staff_name || 'Unassigned' }}</td>
            <td>
              <button class="btn btn-sm btn-warning me-1" @click="editTrek(trek)">Edit</button>
              <button class="btn btn-sm btn-danger me-1" @click="deleteTrek(trek.id)">Delete</button>
              <button class="btn btn-sm btn-info" @click="showAssign(trek)">Assign Staff</button>
            </td>
          </tr>
          <tr v-if="treks.length === 0">
            <td colspan="8" class="text-center text-muted">No treks yet</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Assign Staff Modal -->
    <div v-if="assigningTrek" class="card mt-3">
      <div class="card-body">
        <h5>Assign Staff to "{{ assigningTrek.name }}"</h5>
        <select class="form-select mb-2" v-model="selectedStaffId">
          <option value="">-- No staff (unassign) --</option>
          <option v-for="s in staffList" :key="s.id" :value="s.id">{{ s.name }} ({{ s.email }})</option>
        </select>
        <button class="btn btn-primary me-2" @click="assignStaff">Assign</button>
        <button class="btn btn-secondary" @click="assigningTrek = null">Cancel</button>
      </div>
    </div>

    <router-link to="/admin" class="btn btn-outline-secondary mt-3">← Back to Dashboard</router-link>
  </div>
</template>

<script>
import api from '../../services/api.js'

export default {
  name: 'ManageTreks',
  data() {
    return {
      treks: [],
      staffList: [],
      showForm: false,
      editingTrek: null,
      assigningTrek: null,
      selectedStaffId: '',
      formError: '',
      form: this.emptyForm()
    }
  },
  async created() {
    await this.loadTreks()
    await this.loadStaff()
  },
  methods: {
    emptyForm() {
      return { name: '', location: '', difficulty: 'easy', duration: 1, available_slots: 10, description: '', status: 'pending', start_date: '', end_date: '' }
    },
    async loadTreks() {
      const res = await api.get('/api/admin/treks')
      this.treks = res.data
    },
    async loadStaff() {
      const res = await api.get('/api/admin/staff')
      this.staffList = res.data
    },
    editTrek(trek) {
      this.editingTrek = trek
      this.form = { ...trek }
      this.showForm = true
    },
    async saveTrek() {
      this.formError = ''
      try {
        if (this.editingTrek) {
          await api.put(`/api/admin/treks/${this.editingTrek.id}`, this.form)
        } else {
          await api.post('/api/admin/treks', this.form)
        }
        this.showForm = false
        this.editingTrek = null
        this.form = this.emptyForm()
        await this.loadTreks()
      } catch (err) {
        this.formError = err.response?.data?.error || 'Failed to save trek'
      }
    },
    async deleteTrek(id) {
      if (confirm('Are you sure you want to delete this trek?')) {
        await api.delete(`/api/admin/treks/${id}`)
        await this.loadTreks()
      }
    },
    showAssign(trek) {
      this.assigningTrek = trek
      this.selectedStaffId = trek.assigned_staff || ''
    },
    async assignStaff() {
      await api.put(`/api/admin/treks/${this.assigningTrek.id}/assign`, { staff_id: this.selectedStaffId || null })
      this.assigningTrek = null
      await this.loadTreks()
    },
    statusBadge(status) {
      const map = { pending: 'bg-secondary', approved: 'bg-info', open: 'bg-success', closed: 'bg-warning', completed: 'bg-primary' }
      return map[status] || 'bg-secondary'
    }
  }
}
</script>
