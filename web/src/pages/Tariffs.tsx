import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTariffs, useSubscription, useCreatePayment } from '../hooks/useTariffs';
import TariffCard from '../components/TariffCard';
import { useAuth } from '../hooks/useAuth';

export default function Tariffs() {
    const navigate = useNavigate();
    const { isAuthenticated } = useAuth();
    const [periodFilter, setPeriodFilter] = useState<'week' | 'month'>('month');

    const { data: tariffs = [], isPending, isError, error } = useTariffs();
    const { data: subscription } = useSubscription();
    const paymentMutation = useCreatePayment();

    const handleSelectTariff = async (tariffId: string) => {
        if (!isAuthenticated) {
            window.dispatchEvent(new Event('openLoginModal'));
            return;
        }

        try {
            const result = await paymentMutation.mutateAsync(tariffId);
            if (result.payment_url) {
                window.location.href = result.payment_url;
            } else {
                // Fenik Pay ещё не подключен — заглушка
                alert('Платёжная система Fenik Pay пока не подключена.\nID платежа: ' + result.payment_id);
            }
        } catch {
            // Ошибка показывается ниже
        }
    };

    const filteredTariffs = (tariffs as any[]).filter((t) => t.period === periodFilter);

    if (isPending) {
        return (
            <div className="flex h-[50vh] flex-col items-center justify-center gap-4">
                <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
                <p className="text-muted-foreground font-medium">Загрузка тарифов...</p>
            </div>
        );
    }

    return (
        <div className="flex flex-col gap-10 w-full animate-in fade-in duration-500">
            <div className="text-center max-w-2xl mx-auto space-y-4">
                <h1 className="text-4xl font-bold tracking-tight">Тарифные планы</h1>
                <p className="text-muted-foreground text-lg">
                    Выберите подходящий тариф для доступа к базе проверенных сотрудников
                </p>

                {isAuthenticated && subscription && (
                    <div className="inline-flex items-center gap-3 bg-primary/10 text-primary px-4 py-2 rounded-full font-medium text-sm border border-primary/20">
                        <span className="flex h-2 w-2 rounded-full bg-primary animate-pulse" />
                        Активная подписка: <strong>{subscription.cards_remaining} карточек</strong>
                    </div>
                )}
            </div>

            <div className="flex justify-center">
                <div className="inline-flex p-1 bg-muted rounded-xl border">
                    <button
                        className={`px-6 py-2 rounded-lg text-sm font-medium transition-all ${periodFilter === 'week' ? 'bg-background shadow-sm text-foreground' : 'text-muted-foreground hover:text-foreground'}`}
                        onClick={() => setPeriodFilter('week')}
                    >
                        Неделя
                    </button>
                    <button
                        className={`px-6 py-2 rounded-lg text-sm font-medium transition-all ${periodFilter === 'month' ? 'bg-background shadow-sm text-foreground' : 'text-muted-foreground hover:text-foreground'}`}
                        onClick={() => setPeriodFilter('month')}
                    >
                        Месяц
                    </button>
                </div>
            </div>

            {isError && (
                <div className="bg-destructive/15 text-destructive border border-destructive/30 px-4 py-3 rounded-lg font-medium max-w-md mx-auto">
                    {(error as Error).message}
                </div>
            )}

            {paymentMutation.isError && (
                <div className="bg-destructive/15 text-destructive border border-destructive/30 px-4 py-3 rounded-lg font-medium max-w-md mx-auto">
                    {(paymentMutation.error as Error).message}
                </div>
            )}

            <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-6xl mx-auto w-full px-4">
                {filteredTariffs.map((tariff, index) => (
                    <TariffCard
                        key={tariff.id}
                        tariff={tariff}
                        isPopular={index === 1}
                        onSelect={handleSelectTariff}
                    />
                ))}
            </div>
        </div>
    );
}
