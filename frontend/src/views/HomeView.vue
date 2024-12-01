<template>
  <div class="min-h-screen bg-gray-100 py-12">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="text-center">
        <h1 class="text-4xl font-bold text-gray-900 mb-4">
          Welcome to Recipe Sharing
        </h1>
        <p class="text-xl text-gray-600 mb-8">
          Share your favorite recipes with family and friends
        </p>
        
        <div class="space-x-4">
          <router-link
            v-if="!authStore.token"
            to="/login"
            class="inline-block bg-blue-600 text-white px-6 py-3 rounded-md hover:bg-blue-700"
          >
            Get Started
          </router-link>
          <router-link
            v-else
            to="/recipes"
            class="inline-block bg-blue-600 text-white px-6 py-3 rounded-md hover:bg-blue-700"
          >
            View Recipes
          </router-link>
        </div>
      </div>

      <!-- Features Section -->
      <div class="mt-20 grid grid-cols-1 md:grid-cols-3 gap-8">
        <div class="bg-white p-6 rounded-lg shadow-md">
          <h3 class="text-lg font-semibold mb-2">Share Recipes</h3>
          <p class="text-gray-600">
            Create and share your favorite recipes with detailed instructions and cooking times.
          </p>
        </div>
        
        <div class="bg-white p-6 rounded-lg shadow-md">
          <h3 class="text-lg font-semibold mb-2">Family Groups</h3>
          <p class="text-gray-600">
            Create groups to share recipes with family members and close friends.
          </p>
        </div>
        
        <div class="bg-white p-6 rounded-lg shadow-md">
          <h3 class="text-lg font-semibold mb-2">Easy Access</h3>
          <p class="text-gray-600">
            Access your recipes anywhere, anytime. Perfect for cooking at home or sharing with others.
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useAuthStore } from '@/stores/auth';

const authStore = useAuthStore();
</script>
