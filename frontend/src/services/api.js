import axios from 'axios';
import { supabase } from './supabase';

const api = axios.create({
    baseURL: 'http://localhost:8000',
    headers: {
        'Content-Type': 'application/json'
    },
    withCredentials: true
});

// Request interceptor for API calls
api.interceptors.request.use(
    async (config) => {
        const { data: { session } } = await supabase.auth.getSession();
        const token = session?.access_token;
        
        if (token) {
            config.headers['Authorization'] = `Bearer ${token}`;
        }
        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

// Response interceptor for API calls
api.interceptors.response.use(
    (response) => response,
    async (error) => {
        if (error.response?.status === 401) {
            // Import supabase dynamically to avoid circular dependency
            const { supabase } = await import('./auth');
            await supabase.auth.signOut();
            window.location.href = '/login';
        }
        return Promise.reject(error);
    }
);

export { api };
export const endpoints = {
    // Profile endpoints
    getProfile: () => api.get('/users/me'),
    updateProfile: (profileData) => api.put('/users/me', profileData)
};

// Recipes API
export const recipes = {
    getAll: () => api.get('/recipes'),
    get: (id) => api.get(`/recipes/${id}`),
    create: (recipe) => api.post('/recipes', recipe),
    update: (id, recipe) => api.put(`/recipes/${id}`, recipe),
    delete: (id) => api.delete(`/recipes/${id}`),
    parseImage: (formData) => api.post('/recipes/parse-image', formData, {
        headers: {
            'Content-Type': 'multipart/form-data'
        }
    })
};

// Groups API
export const groups = {
    getAll: () => api.get('/groups'),
    create: (group) => api.post('/groups', group),
    update: (id, group) => api.put(`/groups/${id}`, group),
    delete: (id) => api.delete(`/groups/${id}`),
    getMembers: (groupId) => api.get(`/groups/${groupId}/members`),
    addMember: (groupId, email) => api.post(`/groups/${groupId}/members`, { email }),
    removeMember: (groupId, userId) => api.delete(`/groups/${groupId}/members/${userId}`)
};