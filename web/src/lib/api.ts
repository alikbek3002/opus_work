// ============================================
// API Client — централизованный HTTP клиент
// с авторизацией, error handling и retry
// ============================================

const API_BASE = import.meta.env.VITE_API_URL || '/api';

class ApiError extends Error {
    status: number;
    constructor(message: string, status: number) {
        super(message);
        this.status = status;
        this.name = 'ApiError';
    }
}

async function request<T>(
    endpoint: string,
    options: RequestInit = {}
): Promise<T> {
    const token = localStorage.getItem('access_token');

    const headers: Record<string, string> = {
        'Content-Type': 'application/json',
        ...(options.headers as Record<string, string>),
    };

    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }

    const response = await fetch(`${API_BASE}${endpoint}`, {
        ...options,
        headers,
    });

    if (response.status === 401) {
        // Токен истёк — очищаем и перенаправляем
        localStorage.removeItem('access_token');
        localStorage.removeItem('user_id');
        localStorage.removeItem('user_email');
        window.dispatchEvent(new Event('openLoginModal'));
        throw new ApiError('Сессия истекла', 401);
    }

    if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: 'Ошибка сервера' }));
        throw new ApiError(error.detail || `HTTP ${response.status}`, response.status);
    }

    // Для 204 No Content
    if (response.status === 204) return null as T;

    return response.json();
}

// ============================================
// API методы
// ============================================

export const api = {
    // --- Auth ---
    register: (data: RegisterRequest) =>
        request<AuthResponse>('/auth/register', {
            method: 'POST',
            body: JSON.stringify(data),
        }),

    login: (data: LoginRequest) =>
        request<AuthResponse>('/auth/login', {
            method: 'POST',
            body: JSON.stringify(data),
        }),

    resetPassword: (email: string) =>
        request<{ message: string }>('/auth/reset-password', {
            method: 'POST',
            body: JSON.stringify({ email }),
        }),

    // --- Employees ---
    getEmployees: (params: EmployeeQueryParams = {}) => {
        const searchParams = new URLSearchParams();
        searchParams.set('page', String(params.page ?? 1));
        searchParams.set('limit', String(params.limit ?? 20));
        (params.districts ?? []).forEach((district) => {
            if (district) searchParams.append('district', district);
        });
        (params.specializations ?? []).forEach((specialization) => {
            if (specialization) searchParams.append('specialization', specialization);
        });
        return request<EmployeeCard[]>(`/employees?${searchParams}`);
    },

    getViewedEmployees: () =>
        request<ViewedEmployeesResponse>('/employees/viewed'),

    getViewedHistory: () =>
        request<ViewedEmployeeHistoryItem[]>('/employees/history'),

    viewEmployee: (employeeId: string) =>
        request<EmployeeFullProfile>(`/employees/${employeeId}/view`, { method: 'POST' }),

    // --- Tariffs ---
    getTariffs: () => request<TariffPlan[]>('/tariffs'),

    getSubscription: () => request<Subscription | null>('/tariffs/subscription'),

    // --- Payments ---
    createPayment: (tariffId: string) =>
        request<PaymentResponse>('/payments/create', {
            method: 'POST',
            body: JSON.stringify({ tariff_id: tariffId }),
        }),
};

/**
 * Генерирует URL для получения фото сотрудника
 */
export const getPhotoUrl = (telegramId: number, version?: string | null) => {
    const searchParams = new URLSearchParams();
    if (version) {
        searchParams.set('v', version);
    }
    const suffix = searchParams.toString();
    return `${API_BASE}/photos/${telegramId}${suffix ? `?${suffix}` : ''}`;
};

// ============================================
// Types
// ============================================

// Auth
export interface RegisterRequest {
    email: string;
    password: string;
    full_name: string;
    company_name?: string;
}

export interface LoginRequest {
    email: string;
    password: string;
}

export interface AuthResponse {
    access_token: string;
    user_id: string;
    email: string;
}

// Employees
export interface EmployeeQueryParams {
    page?: number;
    limit?: number;
    districts?: string[];
    specializations?: string[];
}

export type VerificationStatus = 'pending' | 'verified' | 'rejected';
export type ActivitySignal = 'high' | 'medium' | 'low';

export interface EmployeeCard {
    id: string;
    full_name: string;
    gender: string | null;
    age: number | null;
    district: string | null;
    specializations: string | null;
    experience: string | null;
    employment_type: string | null;
    schedule?: string | null;
    ready_for_weekends?: boolean | null;
    has_sanitary_book?: string | null;
    about_me?: string | null;
    has_recommendations?: boolean | null;
    telegram_username?: string | null;
    phone_number?: string | null;
    has_whatsapp?: boolean | null;
    verification_rejected_reason?: string | null;
    verified_by_telegram_id?: number | null;
    opus_experience: string | null;
    is_verified: boolean;
    verification_status: VerificationStatus;
    verification_decided_at: string | null;
    activity_signal: ActivitySignal | null;
    activity_signal_updated_at: string | null;
    contact_opens_count: number;
    telegram_id: number | null;
    created_at: string | null;
}

export interface EmployeeFullProfile extends EmployeeCard {
    telegram_username: string | null;
    phone_number: string | null;
    has_whatsapp: boolean | null;
    photo_file_id: string | null;
    ready_for_weekends: boolean | null;
    has_sanitary_book: string | null;
    about_me: string | null;
    has_recommendations: boolean | null;
    verification_rejected_reason: string | null;
    verified_by_telegram_id: number | null;
    created_at: string | null;
}

export interface ViewedEmployeesResponse {
    viewed_ids: string[];
}

export interface ViewedEmployeeHistoryItem extends EmployeeFullProfile {
    viewed_at: string;
}

// Tariffs
export interface TariffPlan {
    id: string;
    name: string;
    period: string;
    card_limit: number;
    daily_limit?: number | null;
    price: number;
    description: string | null;
}

export interface Subscription {
    id: string;
    tariff_id: string;
    cards_remaining: number;
    daily_limit?: number | null;
    daily_views_used?: number | null;
    daily_views_remaining?: number | null;
    starts_at: string;
    expires_at: string;
    is_active: boolean;
    tariff_plans?: TariffPlan | null;
}

// Payments
export interface PaymentResponse {
    payment_id: string;
    payment_url: string | null;
    status: string;
}
