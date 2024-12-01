<template>
  <div class="min-h-screen bg-gray-100">
    <NavBar />
    <RouterView />
  </div>
</template>

<script setup>
import { onMounted } from 'vue';
import { RouterView } from 'vue-router';
import NavBar from '@/components/NavBar.vue';
import { supabase } from '@/services/supabase';
import { useAuthStore } from '@/stores/auth';
import 'vue-toast-notification/dist/theme-sugar.css';

const authStore = useAuthStore();

onMounted(async () => {
    // Check for existing session
    const { data: { session } } = await supabase.auth.getSession();
    if (session) {
        authStore.session = session;
        authStore.user = session.user;
    }
});
</script>

<style>
@import '@/assets/base.css';
</style>
