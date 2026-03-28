// ============================================
// TanStack Query — конфигурация и кастомные хуки
// Оптимальное кэширование + автоматическая инвалидация
// ============================================

import { QueryClient } from '@tanstack/react-query';

export const queryClient = new QueryClient({
    defaultOptions: {
        queries: {
            // Данные считаются свежими 30 сек — не рефетчим при маунте/фокусе
            staleTime: 30 * 1000,
            // Кэш живёт 5 минут после того как компонент размонтирован
            gcTime: 5 * 60 * 1000,
            // 2 retry на ошибки (кроме 401/403)
            retry: (failureCount, error: any) => {
                if (error?.status === 401 || error?.status === 403) return false;
                return failureCount < 2;
            },
            // Рефетч при возврате на вкладку
            refetchOnWindowFocus: true,
            // Не рефетчить при ремаунте если данные свежие
            refetchOnMount: true,
        },
        mutations: {
            retry: false,
        },
    },
});

// ============================================
// Query Keys — централизованные ключи кэша
// ============================================

export const queryKeys = {
    // Employees
    employees: {
        all: ['employees'] as const,
        list: (filters?: { districts?: string[]; specializations?: string[]; page?: number }) =>
            ['employees', 'list', filters] as const,
        detail: (id: string) => ['employees', 'detail', id] as const,
        viewed: () => ['employees', 'viewed'] as const,
        history: () => ['employees', 'history'] as const,
    },

    // Tariffs
    tariffs: {
        all: ['tariffs'] as const,
        list: () => ['tariffs', 'list'] as const,
    },

    // Subscription
    subscription: {
        current: () => ['subscription', 'current'] as const,
    },

    // Payments
    payments: {
        all: ['payments'] as const,
    },
} as const;
