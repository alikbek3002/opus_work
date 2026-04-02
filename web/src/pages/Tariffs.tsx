import { useTariffs, useSubscription, useCreatePayment } from '../hooks/useTariffs';
import { SquishyPricing } from '../components/ui/squishy-pricing';
import { useAuth } from '../hooks/useAuth';
import { useSearchParams } from 'react-router-dom';

export default function Tariffs() {
    const { isAuthenticated } = useAuth();
    const [searchParams] = useSearchParams();

    const { data: tariffs = [], isPending, isError, error } = useTariffs();
    const { data: subscription } = useSubscription();
    const paymentMutation = useCreatePayment();
    const paymentSuccess = searchParams.get('payment') === 'success';

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
        .filter((t) => t.period === 'day' || t.period === 'week' || t.period === 'month' || t.period === 'quarter')
        .sort((a, b) => {
            const order = { day: 0, week: 1, month: 2, quarter: 3 } as const;
            return order[a.period as 'day' | 'week' | 'month' | 'quarter'] - order[b.period as 'day' | 'week' | 'month' | 'quarter'];
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
            <div className="text-center max-w-2xl mx-auto space-y-4 px-4 sm:px-0 mt-4">
                <div className="inline-block bg-primary/10 border border-primary/20 text-primary font-medium text-sm px-4 py-1 rounded-full mb-2">
                    🔥 Специальные цены 1900/4900/11900 сом действуют только для первых 50 зарегистрированных пользователей!
                </div>
                <h1 className="text-3xl sm:text-4xl font-bold tracking-tight">Тарифные планы</h1>
                <p className="text-muted-foreground text-base sm:text-lg">
                    Найдите нужного кандидата за 15 минут
                </p>

                {isAuthenticated && subscription && (
                    <div className="inline-flex flex-wrap items-center justify-center gap-3 bg-primary/10 text-primary px-4 py-2 rounded-full font-medium text-sm border border-primary/20">
                        <span className="flex h-2 w-2 rounded-full bg-primary animate-pulse" />
                        <span>Активная подписка: <strong>{subscription.cards_remaining} карточек</strong></span>
                        {subscription.daily_limit ? (
                            <span>Сегодня: <strong>{subscription.daily_views_remaining ?? 0}/{subscription.daily_limit}</strong></span>
                        ) : null}
                    </div>
                )}
            </div>

            {paymentSuccess && (
                <div className="bg-primary/10 text-primary border border-primary/30 px-4 py-3 rounded-lg font-medium max-w-2xl mx-auto text-center">
                    Подписка активирована. По акции для первых зарегистрированных осталось 28 тарифов со скидкой.
                </div>
            )}

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
                    isPopularIndex={orderedTariffs.findIndex((tariff) => tariff.period === 'month')}
                />
            </div>
        </div>
    );
}
