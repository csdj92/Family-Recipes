<template>
  <div class="profile-container">
    <v-container>
      <v-row justify="center">
        <v-col cols="12" sm="8" md="6">
          <v-card class="pa-4">
            <v-card-title class="text-h4 mb-4">Profile Settings</v-card-title>
            
            <v-alert
              v-if="error"
              type="error"
              class="mb-4"
              closable
              @click="error = ''"
            >
              {{ error }}
            </v-alert>

            <v-alert
              v-if="success"
              type="success"
              class="mb-4"
              closable
              @click="success = ''"
            >
              {{ success }}
            </v-alert>

            <v-form @submit.prevent="updateProfile" ref="form">
              <v-text-field
                v-model="profile.name"
                label="Name"
                :rules="[v => !!v || 'Name is required']"
                required
              ></v-text-field>

              <v-text-field
                v-model="profile.email"
                label="Email"
                type="email"
                :rules="[
                  v => !!v || 'Email is required',
                  v => /.+@.+\..+/.test(v) || 'Email must be valid'
                ]"
                required
              ></v-text-field>

              <div class="d-flex flex-column gap-4">
                <div class="info-section">
                  <div class="text-subtitle-1 font-weight-bold">Account Status</div>
                  <div class="d-flex align-center mt-2">
                    <v-chip
                      :color="profile.role === 'PREMIUM' ? 'primary' : 'default'"
                      class="mr-2"
                    >
                      {{ profile.role }}
                    </v-chip>
                    <v-chip
                      v-if="profile.is_verified"
                      color="success"
                      class="mr-2"
                    >
                      Verified
                    </v-chip>
                  </div>
                </div>

                <div class="info-section">
                  <div class="text-subtitle-1 font-weight-bold">Member Since</div>
                  <div class="text-body-1 mt-2">
                    {{ new Date(profile.created_at).toLocaleDateString() }}
                  </div>
                </div>
              </div>

              <v-card-actions class="mt-4">
                <v-spacer></v-spacer>
                <v-btn
                  color="primary"
                  type="submit"
                  :loading="loading"
                >
                  Save Changes
                </v-btn>
              </v-card-actions>
            </v-form>
          </v-card>
        </v-col>
      </v-row>
    </v-container>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import api from '@/services/api'

const authStore = useAuthStore()
const form = ref(null)
const loading = ref(false)
const error = ref('')
const success = ref('')

const profile = ref({
  name: '',
  email: '',
  role: '',
  created_at: '',
  is_verified: false
})

async function fetchProfile() {
  try {
    loading.value = true
    const response = await api.get('/users/me')
    profile.value = response.data
  } catch (err) {
    error.value = 'Failed to load profile'
    console.error('Error fetching profile:', err)
  } finally {
    loading.value = false
  }
}

async function updateProfile() {
  if (!form.value.validate()) return

  try {
    loading.value = true
    const response = await api.put('/users/me', {
      name: profile.value.name,
      email: profile.value.email
    })
    profile.value = response.data
    success.value = 'Profile updated successfully'
  } catch (err) {
    error.value = err.response?.data?.detail || 'Failed to update profile'
    console.error('Error updating profile:', err)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchProfile()
})
</script>

<style scoped>
.profile-container {
  padding: 2rem 0;
}

.info-section {
  padding: 1rem;
  background-color: rgba(var(--v-theme-surface-variant), 0.1);
  border-radius: 8px;
}
</style> 