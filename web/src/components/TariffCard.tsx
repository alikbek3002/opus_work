import { type TariffPlan } from '../lib/api';
import * as PricingCard from '@/components/ui/pricing-card';
import { Button } from '@/components/ui/button';
import { CheckCircle2, CopyCheck, Clock } from 'lucide-react';

interface Props {
    tariff: TariffPlan;
    isPopular?: boolean;
    onSelect: (tariffId: string) => void;
}

export default function TariffCard({ tariff, isPopular, onSelect }: Props) {
    const periodLabel = tariff.period === 'day'
        ? 'День'
        : tariff.period === 'week'
            ? 'Неделя'
            : tariff.period === 'month'
                ? 'Месяц'
                : 'Квартал';

    const durationLabel = tariff.period === 'day'
        ? '1 день'
        : tariff.period === 'quarter'
            ? '90 дней'
            : `1 ${periodLabel.toLowerCase()}`;

    return (
        <PricingCard.Card className="flex flex-col h-full">
            <PricingCard.Header glassEffect={isPopular} className={isPopular ? "border-primary/50 shadow-[0_0_20px_rgba(var(--primary),0.2)] bg-primary/5" : ""}>
                <PricingCard.Plan>
                    <PricingCard.PlanName>
                        <CopyCheck className={isPopular ? "text-primary" : "text-muted-foreground"} />
                        <span className={isPopular ? "text-primary font-bold" : "text-foreground font-semibold"}>{tariff.name}</span>
                    </PricingCard.PlanName>
                    {isPopular && (
                        <PricingCard.Badge>Популярный</PricingCard.Badge>
                    )}
                </PricingCard.Plan>

                <PricingCard.Price>
                    <PricingCard.MainPrice>{tariff.price.toLocaleString()}</PricingCard.MainPrice>
                    <span className="text-xl font-bold ml-1">сом</span>
                    <PricingCard.Period>/{tariff.period === 'day' ? 'день' : tariff.period === 'quarter' ? '90 дней' : periodLabel.toLowerCase()}</PricingCard.Period>
                </PricingCard.Price>

                <div className="mt-4 flex-grow">
                    <Button
                        variant={isPopular ? "default" : "outline"}
                        className="w-full font-semibold rounded-xl"
                        onClick={() => onSelect(tariff.id)}
                    >
                        Выбрать тариф
                    </Button>
                </div>
            </PricingCard.Header>

            <PricingCard.Body className="flex-grow">
                {tariff.description && (
                    <PricingCard.Description className="mb-4">
                        {tariff.description}
                    </PricingCard.Description>
                )}

                <PricingCard.List>
                    <PricingCard.ListItem>
                        <CheckCircle2 className="text-primary h-5 w-5 shrink-0" aria-hidden="true" />
                        <span>Доступ к базе: <strong>{tariff.card_limit} карточек</strong></span>
                    </PricingCard.ListItem>
                    <PricingCard.ListItem>
                        <Clock className="text-primary h-5 w-5 shrink-0" aria-hidden="true" />
                        <span>Период действия: <strong>{durationLabel}</strong></span>
                    </PricingCard.ListItem>
                    <PricingCard.ListItem>
                        <CheckCircle2 className="text-primary h-5 w-5 shrink-0" aria-hidden="true" />
                        <span>Доступ ко всем фильтрам</span>
                    </PricingCard.ListItem>
                    <PricingCard.ListItem>
                        <CheckCircle2 className="text-primary h-5 w-5 shrink-0" aria-hidden="true" />
                        <span>Прямые контакты (Telegram/WhatsApp)</span>
                    </PricingCard.ListItem>
                </PricingCard.List>
            </PricingCard.Body>
        </PricingCard.Card>
    );
}
