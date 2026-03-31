import { useTariffs, useSubscription, useCreatePayment } from '../hooks/useTariffs';
import { SquishyPricing } from '../components/ui/squishy-pricing';
import { useAuth } from '../hooks/useAuth';

export default function Tariffs() {
    const { isAuthenticated } = useAuth();

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
            if (!result.payment_url) {
                throw new Error('Не удалось получить ссылку на оплату. Попробуйте ещё раз.');
            }
            window.location.assign(result.payment_url);
        } catch {
            // Ошибка показывается ниже
        }
    };

    const orderedTariffs = (tariffs as any[])
        .filter((t) => t.period === 'week' || t.period === 'month')
        .sort((a, b) => {
            const order = { week: 0, month: 1 } as const;
            return order[a.period as 'week' | 'month'] - order[b.period as 'week' | 'month'];
        });

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
            <div className="text-center max-w-2xl mx-auto space-y-4 px-4 sm:px-0">
                <h1 className="text-3xl sm:text-4xl font-bold tracking-tight">Тарифные планы</h1>
                <p className="text-muted-foreground text-base sm:text-lg">
                    Выберите подходящий тариф для доступа к базе проверенных сотрудников
                </p>

                {isAuthenticated && subscription && (
                    <div className="inline-flex items-center gap-3 bg-primary/10 text-primary px-4 py-2 rounded-full font-medium text-sm border border-primary/20">
                        <span className="flex h-2 w-2 rounded-full bg-primary animate-pulse" />
                        Активная подписка: <strong>{subscription.cards_remaining} карточек</strong>
                    </div>
                )}
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

            <div className="w-full">
                <SquishyPricing
                    tariffs={orderedTariffs}
                    onSelect={handleSelectTariff}
                    isPopularIndex={1}
                />
            </div>
        </div>
    );
}
