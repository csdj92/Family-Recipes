import { createClient } from '@supabase/supabase-js'

const SUPABASE_URL = 'https://cfqmaartpvlexlhchtlm.supabase.co'
const SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImNmcW1hYXJ0cHZsZXhsaGNodGxtIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzI1NDY4NTEsImV4cCI6MjA0ODEyMjg1MX0._THUohooys-XlN9JFDuhvKUDyFLhMeolgRoB0YDDtao'

export const supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY, {
    auth: {
        autoRefreshToken: true,
        persistSession: true,
        detectSessionInUrl: true
    },
    global: {
        headers: {
            'apikey': SUPABASE_ANON_KEY
        }
    }
}) 