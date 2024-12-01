<template>
  <div class="min-h-screen bg-gray-100 flex items-center justify-center">
    <div class="max-w-md w-full bg-white rounded-lg shadow-md p-8">
      <h2 class="text-2xl font-bold mb-6 text-center">Login</h2>
      
      <form @submit.prevent="handleSubmit" class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700">Email</label>
          <input
            v-model="email"
            type="email"
            required
            :disabled="isLoading"
            class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
            placeholder="Enter your email"
          />
        </div>
        
        <div>
          <label class="block text-sm font-medium text-gray-700">Password</label>
          <input
            v-model="password"
            type="password"
            required
            :disabled="isLoading"
            class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
            placeholder="Enter your password"
          />
        </div>

        <div v-if="error" class="text-red-500 text-sm mt-2">
          {{ error }}
        </div>
        
        <button
          type="submit"
          :disabled="isLoading || !email || !password"
          class="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
        >
          <span v-if="isLoading" class="flex items-center">
            <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            Logging in...
          </span>
          <span v-else>Login</span>
        </button>
      </form>
      
      <div class="mt-4 text-center">
        <router-link to="/register" class="text-sm text-blue-600 hover:text-blue-500">
          Don't have an account? Register
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useAuthStore } from '@/stores/auth';
import { useRouter } from 'vue-router';
import { useToast } from 'vue-toast-notification';
import { supabase } from '@/services/supabase';

const email = ref('');
const password = ref('');
const error = ref('');
const isLoading = ref(false);
const authStore = useAuthStore();
const router = useRouter();
const toast = useToast();

onMounted(async () => {
  const { data: { session } } = await supabase.auth.getSession();
  if (session) {
    router.push('/recipes');
  }
});

const handleSubmit = async () => {
  if (!email.value || !password.value) {
    error.value = 'Please enter both email and password';
    return;
  }

  error.value = '';
  isLoading.value = true;
  
  try {
    const { data, error } = await supabase.auth.signInWithPassword({
      email: email.value,
      password: password.value,
    });

    if (error) throw error;

    authStore.session = data.session;
    authStore.user = data.user;

    toast.success('Login successful!');
    router.push('/recipes');
  } catch (err) {
    console.error('Login error:', err);
    error.value = err.message;
    toast.error(error.value);
  } finally {
    isLoading.value = false;
  }
};
</script>

<style scoped>
.v-container {
  background-color: rgb(var(--v-theme-background));
}
</style> 