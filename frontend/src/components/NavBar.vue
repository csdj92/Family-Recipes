<template>
  <nav class="bg-gray-800 text-white p-4">
    <div class="container mx-auto flex justify-between items-center">
      <router-link to="/" class="text-xl font-bold">Recipe Sharing</router-link>
      
      <div class="flex space-x-4">
        <template v-if="authStore.user">
          <router-link to="/recipes" class="hover:text-gray-300">Recipes</router-link>
          <router-link to="/groups" class="hover:text-gray-300">Groups</router-link>
          <button @click="logout" class="hover:text-gray-300">Logout</button>
        </template>
        <template v-else>
          <router-link to="/login" class="hover:text-gray-300">Login</router-link>
          <router-link to="/register" class="hover:text-gray-300">Register</router-link>
        </template>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { useAuthStore } from '@/stores/auth';
import { useRouter } from 'vue-router';

const authStore = useAuthStore();
const router = useRouter();

const logout = async () => {
  authStore.logout();
  router.push('/login');
};
</script> 