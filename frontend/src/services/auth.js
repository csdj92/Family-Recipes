import axios from 'axios';
import { supabase } from './supabase';

// Helper function to handle Supabase errors
function handleSupabaseError(error) {
    if (!error) return null

    console.log('Supabase error:', error)

    // Map Supabase error messages to user-friendly messages
    const errorMap = {
        'User already registered': 'This email is already registered. Please login instead.',
        'Invalid login credentials': 'Invalid email or password.',
        'Email not confirmed': 'Please confirm your email before logging in.',
        'Password should be at least 6 characters': 'Password must be at least 6 characters.',
        'Invalid email': 'Please enter a valid email address.',
        'Email rate limit exceeded': 'Too many attempts. Please try again later.',
        'Email link is invalid or has expired': 'The email link is invalid or has expired. Please request a new one.',
        'Password is too weak': 'Password is too weak. Please choose a stronger password.',
        'User not found': 'Account not found. Please check your email or register.',
    }

    // Check if we have a mapped message for this error
    for (const [key, value] of Object.entries(errorMap)) {
        if (error.message?.toLowerCase().includes(key.toLowerCase())) {
            return new Error(value)
        }
    }

    // Return a generic error message if we don't have a specific mapping
    return new Error(error.message || 'An unexpected error occurred. Please try again.')
}

// Auth functions
export const auth = {
    // Sign up with email and password
    signUp: async ({ email, password, name }) => {
        try {
            console.log('Attempting signup with:', { email, name });
            const { data, error } = await supabase.auth.signUp({
                email,
                password,
                options: {
                    data: {
                        name,
                        avatar_url: null,
                        // Add any other metadata you want to store
                    }
                }
            });
            
            if (error) {
                console.error('Supabase signup error:', error);
                throw handleSupabaseError(error);
            }

            console.log('Signup response:', data);

            // If signup successful but needs email verification
            if (data?.user && !data?.session) {
                return {
                    user: data.user,
                    message: 'Please check your email to confirm your registration.'
                };
            }

            return data;
        } catch (error) {
            console.error('Signup error caught:', error);
            throw handleSupabaseError(error);
        }
    },

    // Sign in with email and password
    signIn: async ({ email, password }) => {
        try {
            const { data, error } = await supabase.auth.signInWithPassword({
                email,
                password
            })
            
            if (error) throw handleSupabaseError(error)
            return data
        } catch (error) {
            throw handleSupabaseError(error)
        }
    },

    // Sign out
    signOut: async () => {
        try {
            const { error } = await supabase.auth.signOut()
            if (error) throw handleSupabaseError(error)
        } catch (error) {
            throw handleSupabaseError(error)
        }
    },

    // Get current session
    getSession: async () => {
        try {
            const { data: { session }, error } = await supabase.auth.getSession()
            if (error) throw handleSupabaseError(error)
            return session
        } catch (error) {
            throw handleSupabaseError(error)
        }
    },

    // Get current user
    getUser: async () => {
        try {
            const { data: { user }, error } = await supabase.auth.getUser()
            if (error) throw handleSupabaseError(error)
            return user
        } catch (error) {
            throw handleSupabaseError(error)
        }
    },

    // Update user profile
    updateProfile: async (updates) => {
        try {
            const { data, error } = await supabase.auth.updateUser({
                data: updates
            })
            if (error) throw handleSupabaseError(error)
            return data
        } catch (error) {
            throw handleSupabaseError(error)
        }
    },

    // Reset password
    resetPassword: async (email) => {
        try {
            const { error } = await supabase.auth.resetPasswordForEmail(email)
            if (error) throw handleSupabaseError(error)
        } catch (error) {
            throw handleSupabaseError(error)
        }
    },

    // Update password
    updatePassword: async (newPassword) => {
        try {
            const { data, error } = await supabase.auth.updateUser({
                password: newPassword
            })
            if (error) throw handleSupabaseError(error)
            return data
        } catch (error) {
            throw handleSupabaseError(error)
        }
    }
}

// Set up auth state change listener
supabase.auth.onAuthStateChange((event, session) => {
    console.log('Auth state changed:', event, session)
}) 