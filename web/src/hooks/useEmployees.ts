// ============================================
// Хуки для работы с сотрудниками
// useQuery — загрузка, useMutation — просмотр карточки
// ============================================

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
    api,
    type EmployeeCard,
    type EmployeeFilters,
    type EmployeeFullProfile,
    type EmployeeQueryParams,
    type EmployeesCountResponse,
    type Subscription,
    type ViewedEmployeeHistoryItem,
    type ViewedEmployeesResponse,
} from '../lib/api';
import { queryKeys } from '../lib/query';

export const EMPLOYEES_PAGE_SIZE = 50;

/**
 * Загрузка списка сотрудников с фильтрами.
 * Кэшируется по ключу [employees, list, filters].
 */
export function useEmployees(filters?: Omit<EmployeeQueryParams, 'limit'>) {
    const sortedDistricts = (filters?.districts ?? []).slice().sort();
    const sortedSpecializations = (filters?.specializations ?? []).slice().sort();

    return useQuery({
        queryKey: queryKeys.employees.list({
            districts: sortedDistricts,
            specializations: sortedSpecializations,
            page: filters?.page,
            limit: EMPLOYEES_PAGE_SIZE,
        }),
        queryFn: () => api.getEmployees({
            page: filters?.page ?? 1,
            limit: EMPLOYEES_PAGE_SIZE,
            districts: sortedDistricts,
            specializations: sortedSpecializations,
        }),
        staleTime: 10 * 1000,
        refetchOnWindowFocus: true,
        refetchOnMount: true,
        // Placeholder пока загружается — показываем пустой массив
        placeholderData: (previousData) => previousData,
    });
}

export function useEmployeesCount(filters?: EmployeeFilters) {
    const sortedDistricts = (filters?.districts ?? []).slice().sort();
    const sortedSpecializations = (filters?.specializations ?? []).slice().sort();

    return useQuery({
        queryKey: queryKeys.employees.count({
            districts: sortedDistricts,
            specializations: sortedSpecializations,
        }),
        queryFn: () => api.getEmployeesCount({
            districts: sortedDistricts,
            specializations: sortedSpecializations,
        }),
        staleTime: 10 * 1000,
        refetchOnWindowFocus: true,
        placeholderData: (previousData: EmployeesCountResponse | undefined) => previousData,
    });
}

export function useViewedEmployees() {
    const token = localStorage.getItem('access_token');

    return useQuery({
        queryKey: queryKeys.employees.viewed(),
        queryFn: () => api.getViewedEmployees(),
        enabled: !!token,
        staleTime: 10 * 1000,
        refetchOnWindowFocus: true,
    });
}

export function useViewedHistory() {
    const token = localStorage.getItem('access_token');

    return useQuery({
        queryKey: queryKeys.employees.history(),
        queryFn: () => api.getViewedHistory(),
        enabled: !!token,
        staleTime: 10 * 1000,
        refetchOnWindowFocus: true,
    });
}

/**
 * Просмотр полного профиля сотрудника.
 * При успехе:
 * - Инвалидирует подписку (обновить остаток карточек)
 * - Возвращает полные данные
 */
export function useViewEmployee() {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: (employeeId: string) => api.viewEmployee(employeeId),
        onSuccess: (data: EmployeeFullProfile, employeeId: string) => {
            queryClient.setQueryData<Subscription | null>(
                queryKeys.subscription.current(),
                (previous) => {
                    if (!previous) return previous;

                    const alreadyViewed = (queryClient.getQueryData<ViewedEmployeesResponse>(
                        queryKeys.employees.viewed()
                    )?.viewed_ids ?? []).includes(employeeId);

                    if (alreadyViewed) return previous;

                    return {
                        ...previous,
                        cards_remaining: Math.max(previous.cards_remaining - 1, 0),
                        daily_views_used:
                            previous.daily_views_used == null
                                ? previous.daily_views_used
                                : previous.daily_views_used + 1,
                        daily_views_remaining:
                            previous.daily_views_remaining == null
                                ? previous.daily_views_remaining
                                : Math.max(previous.daily_views_remaining - 1, 0),
                    };
                }
            );
            // Кэшируем полный профиль
            queryClient.setQueryData(
                queryKeys.employees.detail(employeeId),
                data
            );
            // Инвалидируем подписку — чтобы обновился остаток карточек
            queryClient.invalidateQueries({
                queryKey: queryKeys.subscription.current(),
            });
            queryClient.invalidateQueries({
                queryKey: queryKeys.employees.viewed(),
            });
            queryClient.invalidateQueries({
                queryKey: queryKeys.employees.history(),
            });
            queryClient.setQueryData<ViewedEmployeesResponse | undefined>(
                queryKeys.employees.viewed(),
                (previous) => {
                    const ids = new Set(previous?.viewed_ids ?? []);
                    ids.add(employeeId);
                    return { viewed_ids: Array.from(ids) };
                }
            );
            queryClient.setQueryData<ViewedEmployeeHistoryItem[] | undefined>(
                queryKeys.employees.history(),
                (previous) => {
                    const history = previous ?? [];
                    const existingIndex = history.findIndex((item) => item.id === employeeId);
                    const viewedAt = new Date().toISOString();
                    const nextItem: ViewedEmployeeHistoryItem = {
                        ...data,
                        viewed_at: existingIndex >= 0 ? history[existingIndex].viewed_at : viewedAt,
                    };

                    if (existingIndex >= 0) {
                        const copy = [...history];
                        copy[existingIndex] = { ...copy[existingIndex], ...nextItem };
                        return copy;
                    }

                    return [nextItem, ...history];
                }
            );
        },
    });
}

/**
 * Получить закэшированный полный профиль сотрудника (если просмотрен).
 */
export function useEmployeeProfile(employeeId: string) {
    return useQuery({
        queryKey: queryKeys.employees.detail(employeeId),
        queryFn: () => api.viewEmployee(employeeId),
        enabled: false, // Не загружать автоматически — только по запросу
    });
}
