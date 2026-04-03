// ============================================
// Хуки для тарифов и подписок
// ============================================

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '../lib/api';
import { queryKeys } from '../lib/query';

/**
 * Загрузка тарифных планов.
 * Тарифы обновляются оперативно для промо-акций.
 */
export function useTariffs() {
    return useQuery({
        queryKey: queryKeys.tariffs.list(),
        queryFn: () => api.getTariffs(),
        staleTime: 30 * 1000,
        refetchOnWindowFocus: true,
        refetchOnMount: true,
    });
}

/**
 * Текущая активная подписка работодателя.
 * Обновляется чаще — при каждом просмотре карточки.
 */
export function useSubscription() {
    const token = localStorage.getItem('access_token');
    return useQuery({
        queryKey: queryKeys.subscription.current(),
        queryFn: () => api.getSubscription(),
        staleTime: 30 * 1000, // 30 секунд
        placeholderData: (previousData) => previousData,
        refetchOnWindowFocus: false,
        refetchOnMount: false,
        enabled: !!token, // Не запрашивать, если нет токена
    });
}

/**
 * Создание платежа за тариф.
 * При успехе инвалидирует подписку (если оплата мгновенная).
 */
export function useCreatePayment() {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: (tariffId: string) => api.createPayment(tariffId),
        onSuccess: () => {
            queryClient.invalidateQueries({
                queryKey: queryKeys.subscription.current(),
            });
        },
    });
}
