import { createClient } from '@supabase/supabase-js';

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL;
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY;

export const supabaseClient = (supabaseUrl && supabaseAnonKey)
    ? createClient(supabaseUrl, supabaseAnonKey)
    : null;

export function ensureSupabaseClient() {
    if (!supabaseClient) {
        throw new Error('Не настроены VITE_SUPABASE_URL и VITE_SUPABASE_ANON_KEY.');
    }
    return supabaseClient;
}
