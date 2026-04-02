import { useTariffs, useSubscription, useCreatePayment } from '../hooks/useTariffs';
import { useAuth } from '../hooks/useAuth';
import { useSearchParams } from 'react-router-dom';
import { useState } from 'react';
import { CheckCircle, CreditCard, ShieldCheck } from 'lucide-react';
import * as PricingCard from '../components/ui/pricing-card';
import { Button } from '../components/ui/button';
import { cn } from '@/lib/utils';

export default function Tariffs() {
    const { isAuthenticated } = useAuth();
    const [searchParams] = useSearchParams();
    const [loadingTariffId, setLoadingTariffId] = useState<string | null>(null);

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
            setLoadingTariffId(tariffId);
            const result = await paymentMutation.mutateAsync(tariffId);
            if (!result.payment_url) {
                throw new Error('Не удалось получить ссылку на оплату. Попробуйте ещё раз.');
            }
            window.location.assign(result.payment_url);
        } catch {
            // Ошибка показывается ниже
        } finally {
            setLoadingTariffId(null);
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

    const getDurationText = (period: string) => {
        const texts: Record<string, string> = {
            day: '1 день',
            week: '7 дней',
            month: '30 дней',
            quarter: '90 дней'
        };
        return texts[period] || period;
    };

    return (
        <div className="flex flex-col gap-10 w-full animate-in fade-in duration-500 py-12">
            <div className="text-center max-w-2xl mx-auto space-y-4 px-4 sm:px-0">
                <h1 className="text-3xl sm:text-4xl font-bold tracking-tight">Тарифные планы</h1>
                <p className="text-muted-foreground text-base sm:text-lg">
                    Найдите нужного кандидата за 15 минут
                </p>

                {isAuthenticated && subscription && (
                    <div className="mt-6 inline-flex flex-wrap items-center justify-center gap-3 bg-primary/10 text-primary px-4 py-2 rounded-full font-medium text-sm border border-primary/20">
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
                    Подписка успешно активирована. Спасибо за выбор нашего сервиса!
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

            <div className="w-full max-w-6xl mx-auto px-4">
                <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4 justify-center items-stretch">
                    {orderedTariffs.map((tariff) => {
                        const isPopular = tariff.period === 'month';
                        const isLoading = loadingTariffId === tariff.id;

                        return (
                            <PricingCard.Card
                                key={tariff.id}
                                className={cn(
                                    "flex flex-col h-full w-full max-w-[300px] mx-auto",
                                    isPopular ? "border-primary/50 shadow-primary/10 md:scale-105 z-10" : "border-border/50"
                                )}
                            >
                                <PricingCard.Header glassEffect={isPopular} className={cn("flex-none", isPopular ? "bg-primary/5 dark:bg-primary/5" : "")}>
                                    <PricingCard.Plan>
                                        <PricingCard.PlanName>
                                            <ShieldCheck className={cn("w-4 h-4", isPopular ? "text-primary" : "")} />
                                            <span className={cn(isPopular ? "text-primary font-semibold" : "")}>{tariff.name}</span>
                                        </PricingCard.PlanName>
                                        {isPopular && (
                                            <PricingCard.Badge className="bg-primary/10 text-primary border-primary/20">Популярный</PricingCard.Badge>
                                        )}
                                    </PricingCard.Plan>
                                    <PricingCard.Price>
                                        <PricingCard.MainPrice>{tariff.price.toLocaleString()}</PricingCard.MainPrice>
                                        <PricingCard.Period>сом / {getDurationText(tariff.period)}</PricingCard.Period>
                                    </PricingCard.Price>
                                    <Button
                                        variant={isPopular ? "default" : "outline"}
                                        className="w-full mt-4 font-semibold group relative overflow-hidden"
                                        onClick={() => handleSelectTariff(tariff.id)}
                                        disabled={isLoading}
                                    >
                                        {isLoading ? (
                                            <div className="flex items-center gap-2">
                                                <span className="h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent" />
                                                Оформление...
                                            </div>
                                        ) : (
                                            <div className="flex items-center gap-2">
                                                <CreditCard className="w-4 h-4" />
                                                <span>Выбрать тариф</span>
                                            </div>
                                        )}
                                    </Button>
                                </PricingCard.Header>

                                <PricingCard.Body className="flex flex-col flex-1 pb-6">
                                    <PricingCard.Description className="mb-4">
                                        {tariff.description || `Доступ к базе проверенных кандидатов на ${getDurationText(tariff.period)}.`}
                                    </PricingCard.Description>
                                    <PricingCard.List className="mt-auto">
                                        <PricingCard.ListItem>
                                            <CheckCircle className="text-primary w-4 h-4 mt-0.5 shrink-0" aria-hidden="true" />
                                            <span><strong>{tariff.card_limit}</strong> открытий контактов</span>
                                        </PricingCard.ListItem>
                                        <PricingCard.ListItem>
                                            <CheckCircle className="text-primary w-4 h-4 mt-0.5 shrink-0" aria-hidden="true" />
                                            <span><strong>{getDurationText(tariff.period)}</strong> доступа</span>
                                        </PricingCard.ListItem>
                                        {tariff.period !== 'day' && (
                                            <PricingCard.ListItem>
                                                <CheckCircle className="text-primary w-4 h-4 mt-0.5 shrink-0" aria-hidden="true" />
                                                <span>Умный поиск кандидатов</span>
                                            </PricingCard.ListItem>
                                        )}
                                    </PricingCard.List>
                                </PricingCard.Body>
                            </PricingCard.Card>
                        );
                    })}
                </div>
            </div>
        </div>
    );
}
