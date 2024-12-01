<template>
  <div class="min-h-screen bg-gray-100 flex items-center justify-center">
    <div class="max-w-md w-full bg-white rounded-lg shadow-md p-8">
      <h2 class="text-2xl font-bold mb-6 text-center">Register</h2>
      
      <form @submit.prevent="handleSubmit" class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700">Name</label>
          <input
            v-model="form.name"
            type="text"
            required
            class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
          />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700">Email</label>
          <input
            v-model="form.email"
            type="email"
            required
            class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
          />
        </div>
        
        <div>
          <label class="block text-sm font-medium text-gray-700">Password</label>
          <input
            v-model="form.password"
            type="password"
            required
            class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
          />
        </div>
        
        <button
          type="submit"
          class="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
        >
          Register
        </button>
      </form>
      
      <div class="mt-4 text-center">
        <router-link to="/login" class="text-sm text-blue-600 hover:text-blue-500">
          Already have an account? Login
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useAuthStore } from '@/stores/auth';
import { useRouter } from 'vue-router';
import { useToast } from 'vue-toast-notification';

const form = ref({
  name: '',
  email: '',
  password: '',
});

const authStore = useAuthStore();
const router = useRouter();
const toast = useToast();

const handleSubmit = async () => {
  try {
    const result = await authStore.signup({
      email: form.value.email,
      password: form.value.password,
      name: form.value.name
    });
    
    if (result.message) {
      toast.success(result.message);
      router.push('/login');
    } else {
      toast.success('Registration successful!');
      router.push('/recipes');
    }
  } catch (error) {
    console.error('Registration error:', error);
    toast.error(error.message || 'Registration failed. Please try again.');
  }
};
</script> 