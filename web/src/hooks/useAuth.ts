// ============================================
// Хук авторизации
// ============================================

import { useState, useCallback, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useQueryClient } from '@tanstack/react-query';
import { api, type RegisterRequest, type LoginRequest } from '../lib/api';

export function useAuth() {
    const navigate = useNavigate();
    const queryClient = useQueryClient();
    const [isAuthenticated, setIsAuthenticated] = useState(() => !!localStorage.getItem('access_token'));
    const [userEmail, setUserEmail] = useState(() => localStorage.getItem('user_email'));
    const [userId, setUserId] = useState(() => localStorage.getItem('user_id'));
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    // Слушаем изменения localStorage (для синхронизации вкладок) и кастомный эвент auth_changed (для текущего окна)
    useEffect(() => {
        const handleAuthChange = () => {
            setIsAuthenticated(!!localStorage.getItem('access_token'));
            setUserEmail(localStorage.getItem('user_email'));
            setUserId(localStorage.getItem('user_id'));
        };
        window.addEventListener('storage', handleAuthChange);
        window.addEventListener('auth_changed', handleAuthChange);
        return () => {
            window.removeEventListener('storage', handleAuthChange);
            window.removeEventListener('auth_changed', handleAuthChange);
        };
    }, []);

    const login = useCallback(async (data: LoginRequest) => {
        setLoading(true);
        setError('');
        try {
            const response = await api.login(data);
            localStorage.setItem('access_token', response.access_token);
            localStorage.setItem('user_id', response.user_id);
            localStorage.setItem('user_email', response.email);
            window.dispatchEvent(new Event('auth_changed'));
            navigate('/');
        } catch (err: any) {
            setError(err.message || 'Ошибка авторизации');
            throw err;
        } finally {
            setLoading(false);
        }
    }, [navigate]);

    const register = useCallback(async (data: RegisterRequest) => {
        setLoading(true);
        setError('');
        try {
            const response = await api.register(data);
            localStorage.setItem('access_token', response.access_token);
            localStorage.setItem('user_id', response.user_id);
            localStorage.setItem('user_email', response.email);
            window.dispatchEvent(new Event('auth_changed'));
            navigate('/');
        } catch (err: any) {
            setError(err.message || 'Ошибка регистрации');
            throw err;
        } finally {
            setLoading(false);
        }
    }, [navigate]);

    const logout = useCallback(() => {
        localStorage.removeItem('access_token');
        localStorage.removeItem('user_id');
        localStorage.removeItem('user_email');
        window.dispatchEvent(new Event('auth_changed'));
        // Очищаем весь кэш React Query
        queryClient.clear();
        navigate('/');
    }, [navigate, queryClient]);

    return { isAuthenticated, userEmail, userId, loading, error, login, register, logout, setError };
}
