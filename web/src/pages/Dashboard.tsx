import { useEffect, useMemo, useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { ChevronLeft, ChevronRight, Filter } from 'lucide-react';
import { EMPLOYEES_PAGE_SIZE, useEmployees, useEmployeesCount, useViewedEmployees, useViewedHistory, useViewEmployee } from '../hooks/useEmployees';
import { useSubscription } from '../hooks/useTariffs';
import EmployeeCard from '../components/EmployeeCard';
import EmployeeDetailsDialog from '../components/EmployeeDetailsDialog';
import MultiSelectDropdown from '../components/MultiSelectDropdown';
import { useAuth } from '../hooks/useAuth';
import { type EmployeeCard as EmployeeCardType, type EmployeeFullProfile } from '../lib/api';
import { EMPLOYEE_DISTRICT_OPTIONS, EMPLOYEE_SPECIALIZATION_OPTIONS } from '../lib/employee-options';

type PaginationItem = number | 'ellipsis-left' | 'ellipsis-right';

function buildPagination(currentPage: number, totalPages: number): PaginationItem[] {
    if (totalPages <= 1) return [1];

    const pages = new Set<number>([1, totalPages, currentPage - 1, currentPage, currentPage + 1]);
    const sortedPages = Array.from(pages)
        .filter((page) => page >= 1 && page <= totalPages)
        .sort((a, b) => a - b);

    const items: PaginationItem[] = [];
    sortedPages.forEach((page, index) => {
        if (index > 0) {
            const previousPage = sortedPages[index - 1];
            if (page - previousPage > 1) {
                items.push(index === 1 ? 'ellipsis-left' : 'ellipsis-right');
            }
        }
        items.push(page);
    });

    return items;
}

function isFreshProfile(
    employee: EmployeeCardType | null,
    profile?: EmployeeFullProfile | null,
) {
    if (!employee || !profile) return false;
    if (!employee.created_at || !profile.created_at) return true;
    return employee.created_at === profile.created_at;
}

export default function Dashboard() {
    const navigate = useNavigate();
    const { isAuthenticated } = useAuth();
    const [currentPage, setCurrentPage] = useState(1);
    const [searchDistricts, setSearchDistricts] = useState<string[]>([]);
    const [searchSpecs, setSearchSpecs] = useState<string[]>([]);
    const [appliedFilters, setAppliedFilters] = useState<{ districts?: string[]; specializations?: string[] }>({});
    const [selectedEmployee, setSelectedEmployee] = useState<EmployeeCardType | null>(null);
    const [openedProfiles, setOpenedProfiles] = useState<Record<string, EmployeeFullProfile>>({});
    const [isFiltersOpen, setIsFiltersOpen] = useState(false);

    const { data: employees = [], isPending, error, isError } = useEmployees({
        ...appliedFilters,
        page: currentPage,
    });
    const { data: employeesCount } = useEmployeesCount(appliedFilters);
    const { data: subscription } = useSubscription();
    const { data: viewedEmployees } = useViewedEmployees();
    const { data: viewedHistory = [] } = useViewedHistory();
    const viewMutation = useViewEmployee();
    const totalEmployees = employeesCount?.count ?? employees.length;
    const totalPages = Math.max(Math.ceil(totalEmployees / EMPLOYEES_PAGE_SIZE), 1);
    const paginationPages = useMemo(() => buildPagination(currentPage, totalPages), [currentPage, totalPages]);
    const viewedIds = useMemo(() => new Set(viewedEmployees?.viewed_ids ?? []), [viewedEmployees]);
    const viewedProfilesMap = useMemo(() => {
        const map: Record<string, EmployeeFullProfile> = {};
        viewedHistory.forEach((item) => {
            const { viewed_at: _viewedAt, ...profile } = item;
            map[item.id] = profile;
        });
        return map;
    }, [viewedHistory]);
    const selectedProfile = selectedEmployee
        ? (
            (isFreshProfile(selectedEmployee, openedProfiles[selectedEmployee.id])
                ? openedProfiles[selectedEmployee.id]
                : null)
            ?? (isFreshProfile(selectedEmployee, viewedProfilesMap[selectedEmployee.id])
                ? viewedProfilesMap[selectedEmployee.id]
                : null)
        )
        : null;
    const unlockError = viewMutation.isError ? (viewMutation.error as Error).message : null;

    const handleSearch = useCallback(() => {
        setCurrentPage(1);
        setAppliedFilters({
            districts: searchDistricts.length ? searchDistricts : undefined,
            specializations: searchSpecs.length ? searchSpecs : undefined,
        });
    }, [searchDistricts, searchSpecs]);

    const handleResetFilters = useCallback(() => {
        setCurrentPage(1);
        setSearchDistricts([]);
        setSearchSpecs([]);
        setAppliedFilters({});
    }, []);

    useEffect(() => {
        if (currentPage > totalPages) {
            setCurrentPage(totalPages);
        }
    }, [currentPage, totalPages]);

    const handleOpenEmployee = useCallback((employee: EmployeeCardType) => {
        setSelectedEmployee(employee);

        if (!isAuthenticated || !viewedIds.has(employee.id)) {
            return;
        }

        void viewMutation.mutateAsync(employee.id)
            .then((profile) => {
                setOpenedProfiles((prev) => ({
                    ...prev,
                    [employee.id]: profile,
                }));
            })
            .catch(() => {
                // Тихо игнорируем: старые данные уже есть в кэше истории.
            });
    }, [isAuthenticated, viewedIds, viewMutation]);

    const handleViewEmployee = useCallback(async (employeeId: string) => {
        if (!isAuthenticated) {
            window.dispatchEvent(new Event('openLoginModal'));
            return;
        }

        const alreadyViewed = viewedIds.has(employeeId);

        if (!alreadyViewed && (!subscription || subscription.cards_remaining <= 0)) {
            navigate('/tariffs');
            return;
        }

        try {
            const profile = await viewMutation.mutateAsync(employeeId);
            setOpenedProfiles((prev) => ({
                ...prev,
                [employeeId]: profile,
            }));
        } catch (err: any) {
            if (err.status === 403) {
                navigate('/tariffs');
            }
        }
    }, [isAuthenticated, navigate, subscription, viewMutation, viewedIds]);

    if (isPending) {
        return (
            <div className="flex h-[50vh] flex-col items-center justify-center gap-4">
                <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
                <p className="text-muted-foreground font-medium">Загрузка анкет...</p>
            </div>
        );
    }

    return (
        <div className="flex flex-col gap-8 w-full">
            <div className="flex flex-row justify-between items-start md:items-center gap-4">
                <div>
                    <h1 className="text-2xl sm:text-3xl font-bold tracking-tight">Анкеты</h1>
                    <p className="text-muted-foreground mt-1">Найдите нужного сотрудника за 15 минут</p>
                </div>
                <button
                    className="md:hidden flex items-center justify-center gap-2 rounded-xl border border-border/50 bg-card px-4 py-2 text-sm font-medium shadow-sm hover:bg-muted"
                    onClick={() => setIsFiltersOpen(!isFiltersOpen)}
                >
                    <Filter className="w-4 h-4 shrink-0" />
                    <span>{isFiltersOpen ? "Скрыть" : "Фильтры"}</span>
                </button>
            </div>

            <div className={`grid-cols-1 md:grid-cols-2 gap-6 bg-card border border-border/50 rounded-2xl p-4 sm:p-6 shadow-sm relative ${isFiltersOpen ? 'grid' : 'hidden md:grid'}`}>
                <div className="absolute inset-0 overflow-hidden rounded-2xl pointer-events-none">
                    <div className="absolute top-0 right-0 -m-8 w-32 h-32 bg-primary/5 rounded-full blur-2xl" />
                    <div className="absolute bottom-0 left-0 -m-8 w-32 h-32 bg-primary/5 rounded-full blur-2xl" />
                </div>

                <div className="relative z-30 w-full space-y-1">
                    <MultiSelectDropdown
                        label="Районы"
                        placeholder="Выберите районы"
                        options={EMPLOYEE_DISTRICT_OPTIONS}
                        selectedValues={searchDistricts}
                        onChange={setSearchDistricts}
                        helperText="Можно выбрать несколько районов без закрытия списка"
                    />
                </div>

                <div className="relative z-20 w-full space-y-1">
                    <MultiSelectDropdown
                        label="Профессии"
                        placeholder="Выберите профессии"
                        options={EMPLOYEE_SPECIALIZATION_OPTIONS}
                        selectedValues={searchSpecs}
                        onChange={setSearchSpecs}
                        helperText="Можно выбрать несколько специализаций без закрытия списка"
                    />
                </div>

                <div className="md:col-span-2 flex flex-col sm:flex-row gap-3 mt-2 relative z-10 w-full">
                    <button
                        onClick={handleSearch}
                        className="inline-flex items-center justify-center whitespace-nowrap rounded-xl text-sm font-semibold transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 bg-primary text-primary-foreground hover:bg-primary/90 shadow-md h-11 px-6 py-2 w-full sm:w-auto"
                    >
                        Найти анкеты
                    </button>
                    <button
                        onClick={handleResetFilters}
                        className="inline-flex items-center justify-center whitespace-nowrap rounded-xl text-sm font-semibold transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 border border-input bg-background hover:bg-muted hover:text-foreground h-11 px-6 py-2 w-full sm:w-auto"
                    >
                        Сбросить фильтры
                    </button>
                </div>
            </div>

            {isError && (
                <div className="bg-destructive/15 text-destructive border border-destructive/30 px-4 py-3 rounded-lg font-medium">
                    {(error as Error).message}
                </div>
            )}

            <div className="flex flex-col gap-2 rounded-2xl border border-border/50 bg-card px-4 py-4 shadow-sm sm:flex-row sm:items-center sm:justify-between sm:px-5">
                <div>
                    <p className="text-sm font-semibold text-foreground">
                        Найдено анкет: {totalEmployees}
                    </p>
                    <p className="text-sm text-muted-foreground">
                        Страница {Math.min(currentPage, totalPages)} из {totalPages}
                    </p>
                </div>
                <p className="text-sm text-muted-foreground">
                    Загружаем по {EMPLOYEES_PAGE_SIZE} карточки за раз, чтобы список открывался быстрее.
                </p>
            </div>

            {employees.length === 0 ? (
                <div className="flex flex-col items-center justify-center py-10 sm:py-20 px-4 text-center border border-border/50 rounded-2xl bg-card shadow-sm">
                    <span className="text-5xl mb-4">🔍</span>
                    <h3 className="text-xl font-semibold mb-2">Не найдено ни одной анкеты</h3>
                    <p className="text-muted-foreground">Попробуйте изменить параметры поиска или загляните позже.</p>
                </div>
            ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-8">
                    {employees.map((emp) => (
                        <EmployeeCard
                            key={emp.id}
                            employee={emp}
                            onOpen={handleOpenEmployee}
                            isViewed={viewedIds.has(emp.id)}
                        />
                    ))}
                </div>
            )}

            {totalPages > 1 && (
                <div className="flex flex-col gap-3 rounded-2xl border border-border/50 bg-card px-4 py-4 shadow-sm sm:flex-row sm:items-center sm:justify-between sm:px-5">
                    <p className="text-sm text-muted-foreground">
                        Показаны анкеты {(currentPage - 1) * EMPLOYEES_PAGE_SIZE + 1}-{Math.min(currentPage * EMPLOYEES_PAGE_SIZE, totalEmployees)} из {totalEmployees}
                    </p>
                    <div className="flex items-center gap-2">
                        <button
                            type="button"
                            onClick={() => setCurrentPage((page) => Math.max(page - 1, 1))}
                            disabled={currentPage === 1}
                            className="inline-flex h-10 items-center justify-center gap-2 rounded-xl border border-input bg-background px-4 text-sm font-medium transition-colors hover:bg-muted disabled:cursor-not-allowed disabled:opacity-50"
                        >
                            <ChevronLeft className="h-4 w-4" />
                            Назад
                        </button>

                        <div className="rounded-xl border border-border/60 bg-muted/40 px-4 py-2 text-sm font-semibold text-foreground">
                            {currentPage} / {totalPages}
                        </div>

                        <div className="hidden items-center gap-2 md:flex">
                            {paginationPages.map((item) => (
                                typeof item === 'number' ? (
                                    <button
                                        key={item}
                                        type="button"
                                        onClick={() => setCurrentPage(item)}
                                        className={`inline-flex h-10 min-w-10 items-center justify-center rounded-xl border px-3 text-sm font-semibold transition-colors ${
                                            item === currentPage
                                                ? 'border-primary bg-primary text-primary-foreground'
                                                : 'border-input bg-background hover:bg-muted'
                                        }`}
                                    >
                                        {item}
                                    </button>
                                ) : (
                                    <span
                                        key={item}
                                        className="inline-flex h-10 min-w-10 items-center justify-center text-sm font-semibold text-muted-foreground"
                                    >
                                        ...
                                    </span>
                                )
                            ))}
                        </div>

                        <button
                            type="button"
                            onClick={() => setCurrentPage((page) => Math.min(page + 1, totalPages))}
                            disabled={currentPage === totalPages}
                            className="inline-flex h-10 items-center justify-center gap-2 rounded-xl border border-input bg-background px-4 text-sm font-medium transition-colors hover:bg-muted disabled:cursor-not-allowed disabled:opacity-50"
                        >
                            Вперёд
                            <ChevronRight className="h-4 w-4" />
                        </button>
                    </div>
                </div>
            )}

            <EmployeeDetailsDialog
                open={!!selectedEmployee}
                onOpenChange={(open) => !open && setSelectedEmployee(null)}
                employee={selectedEmployee}
                unlockedProfile={selectedProfile}
                isAuthenticated={isAuthenticated}
                isViewed={selectedEmployee ? viewedIds.has(selectedEmployee.id) : false}
                isUnlocking={viewMutation.isPending && viewMutation.variables === selectedEmployee?.id}
                remainingCards={subscription?.cards_remaining ?? null}
                dailyRemaining={subscription?.daily_views_remaining ?? null}
                dailyLimit={subscription?.daily_limit ?? null}
                unlockError={unlockError}
                onRequestLogin={() => window.dispatchEvent(new Event('openLoginModal'))}
                onUnlock={handleViewEmployee}
            />
        </div>
    );
}
