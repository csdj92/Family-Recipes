import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { auth } from '@/services/auth';

export const useAuthStore = defineStore('auth', () => {
    const user = ref(null);
    const session = ref(null);
    const loading = ref(true);

    const token = computed(() => session.value?.access_token);

    const isAuthenticated = computed(() => !!session.value);

    async function initialize() {
        try {
            loading.value = true;
            session.value = await auth.getSession();
            if (session.value) {
                user.value = session.value.user;
            }
        } catch (error) {
            console.error('Error initializing auth:', error);
        } finally {
            loading.value = false;
        }
    }

    async function login(credentials) {
        try {
            loading.value = true;
            const data = await auth.signIn(credentials);
            session.value = data.session;
            user.value = data.user;
            return data;
        } catch (error) {
            console.error('Login error:', error);
            throw error;
        } finally {
            loading.value = false;
        }
    }

    async function signup(userData) {
        try {
            loading.value = true;
            const data = await auth.signUp({
                email: userData.email,
                password: userData.password,
                name: userData.name
            });
            
            if (data.message) {
                // Email confirmation required
                return data;
            } else if (data.session) {
                // Auto-sign in enabled
                session.value = data.session;
                user.value = data.user;
            }
            return data;
        } catch (error) {
            console.error('Signup error:', error);
            throw error;
        } finally {
            loading.value = false;
        }
    }

    async function logout() {
        try {
            loading.value = true;
            await auth.signOut();
            user.value = null;
            session.value = null;
        } catch (error) {
            console.error('Logout error:', error);
            throw error;
        } finally {
            loading.value = false;
        }
    }

    async function updateProfile(updates) {
        try {
            loading.value = true;
            const data = await auth.updateProfile(updates);
            user.value = data.user;
            return data;
        } catch (error) {
            console.error('Profile update error:', error);
            throw error;
        } finally {
            loading.value = false;
        }
    }

    // Initialize auth state
    initialize();

    return {
        user,
        session,
        token,
        loading,
        isAuthenticated,
        login,
        signup,
        logout,
        updateProfile
    };
}); 