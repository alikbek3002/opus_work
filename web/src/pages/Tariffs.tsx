import { useTariffs, useSubscription, useCreatePayment } from '../hooks/useTariffs';
import { useAuth } from '../hooks/useAuth';
import { useSearchParams } from 'react-router-dom';
import { useState } from 'react';
import { CheckCircle, CreditCard, Flame, Lock, ShieldCheck } from 'lucide-react';
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

    const orderedTariffs = tariffs
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

    const getContactsText = (count: number) => {
        const mod10 = count % 10;
        const mod100 = count % 100;
        if (mod100 >= 11 && mod100 <= 14) return 'контактов';
        if (mod10 === 1) return 'контакт';
        if (mod10 >= 2 && mod10 <= 4) return 'контакта';
        return 'контактов';
    };

    const audienceByPeriod: Record<string, string> = {
        day: 'Попробовать сервис',
        week: 'Закрыть срочную вакансию',
        month: 'Регулярный найм персонала',
        quarter: 'Постоянная потребность в кадрах',
    };

    const originalPriceByPeriod: Record<string, string | null> = {
        day: '690',
        week: '2,900',
        month: '7,900',
        quarter: '19,900',
    };

    const discountByPeriod: Record<string, string | null> = {
        day: '29%',
        week: '34%',
        month: '45%',
        quarter: '40%',
    };

    return (
        <div className="flex flex-col gap-10 w-full animate-in fade-in duration-500 py-12">
            <div className="text-center max-w-2xl mx-auto space-y-4 px-4 sm:px-0">
                <h1 className="text-3xl sm:text-4xl font-bold tracking-tight">Тарифные планы</h1>
                <p className="text-muted-foreground text-base sm:text-lg">
                    Найдите нужного сотрудника за 15 минут
                </p>
                <div className="rounded-3xl border border-orange-200 bg-[linear-gradient(135deg,rgba(255,247,237,1),rgba(255,237,213,1))] px-5 py-5 shadow-[0_18px_50px_rgba(249,115,22,0.12)] sm:px-7 sm:py-6">
                    <div className="flex flex-col items-center gap-3 text-center">
                        <div className="inline-flex items-center gap-2 rounded-full border border-orange-300/70 bg-white/80 px-4 py-1.5 text-xs font-extrabold uppercase tracking-[0.22em] text-orange-700">
                            <Flame className="h-3.5 w-3.5" />
                            Ранний доступ · Первые 50 клиентов
                        </div>
                        <p className="text-sm font-semibold text-orange-900 sm:text-base">
                            Скидки до 45% фиксируется навсегда при продлении
                        </p>
                    </div>
                </div>

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
                        const discount = discountByPeriod[tariff.period] ?? null;
                        const originalPrice = originalPriceByPeriod[tariff.period] ?? null;
                        const audience = audienceByPeriod[tariff.period] ?? 'Подходящий вариант для найма';

                        return (
                            <PricingCard.Card
                                key={tariff.id}
                                className={cn(
                                    "flex flex-col h-full w-full max-w-[300px] mx-auto",
                                    isPopular ? "border-primary/50 shadow-primary/10 md:scale-[1.03] z-10" : "border-border/50"
                                )}
                            >
                                <PricingCard.Header
                                    glassEffect={isPopular}
                                    className={cn(
                                        "flex-none",
                                        isPopular
                                            ? "bg-[linear-gradient(180deg,rgba(239,246,255,1),rgba(255,255,255,1))]"
                                            : "bg-[linear-gradient(180deg,rgba(248,250,252,1),rgba(255,255,255,1))]"
                                    )}
                                >
                                    <PricingCard.Plan className="items-start">
                                        <PricingCard.PlanName>
                                            <ShieldCheck className={cn("w-4 h-4", isPopular ? "text-primary" : "")} />
                                            <span className={cn(isPopular ? "text-primary font-semibold" : "")}>{tariff.name}</span>
                                        </PricingCard.PlanName>
                                        <div className="flex flex-wrap items-center justify-end gap-2">
                                            {isPopular && (
                                                <PricingCard.Badge className="bg-primary/10 text-primary border-primary/20">Популярный</PricingCard.Badge>
                                            )}
                                            {discount && (
                                                <PricingCard.Badge className="bg-emerald-100 text-emerald-700 border-emerald-200">
                                                    Скидка {discount}
                                                </PricingCard.Badge>
                                            )}
                                        </div>
                                    </PricingCard.Plan>
                                    <div className="mb-5">
                                        <p className="text-sm font-medium text-muted-foreground">Для кого</p>
                                        <p className="mt-1 text-base font-semibold text-foreground">{audience}</p>
                                    </div>
                                    <PricingCard.Price className="items-baseline">
                                        <div className="flex flex-col">
                                            <div className="flex items-baseline gap-2">
                                                {originalPrice && <PricingCard.OriginalPrice>{originalPrice}</PricingCard.OriginalPrice>}
                                                <PricingCard.MainPrice>{tariff.price.toLocaleString()}</PricingCard.MainPrice>
                                                <span className="text-xl font-bold ml-1">сом</span>
                                            </div>
                                            <PricingCard.Period>за {getDurationText(tariff.period)}</PricingCard.Period>
                                        </div>
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
                                    <PricingCard.List className="mt-auto">
                                        <PricingCard.ListItem>
                                            <CheckCircle className="text-primary w-4 h-4 mt-0.5 shrink-0" aria-hidden="true" />
                                            <span><strong>{tariff.card_limit}</strong> {getContactsText(tariff.card_limit)}</span>
                                        </PricingCard.ListItem>
                                        {tariff.daily_limit && (
                                            <PricingCard.ListItem>
                                                <CheckCircle className="text-primary w-4 h-4 mt-0.5 shrink-0" aria-hidden="true" />
                                                <span>До <strong>{tariff.daily_limit}</strong> в день</span>
                                            </PricingCard.ListItem>
                                        )}
                                        <PricingCard.ListItem>
                                            <CheckCircle className="text-primary w-4 h-4 mt-0.5 shrink-0" aria-hidden="true" />
                                            <span><strong>{getDurationText(tariff.period)}</strong> доступа</span>
                                        </PricingCard.ListItem>
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
