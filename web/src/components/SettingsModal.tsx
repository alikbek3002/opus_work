import { useState } from "react";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { api } from "@/lib/api";
import { useSubscription } from "@/hooks/useTariffs";
import { useViewedHistory } from "@/hooks/useEmployees";
import VerificationBadge from "@/components/VerificationBadge";

interface SettingsModalProps {
    isOpen: boolean;
    onClose: () => void;
    userEmail?: string;
}

export default function SettingsModal({ isOpen, onClose, userEmail }: SettingsModalProps) {
    const [loading, setLoading] = useState(false);
    const [successMsg, setSuccessMsg] = useState("");
    const [errorMsg, setErrorMsg] = useState("");
    const { data: subscription, isLoading: subLoading } = useSubscription();
    const { data: viewedHistory = [], isLoading: historyLoading } = useViewedHistory();

    const formatViewedAt = (value: string) =>
        new Date(value).toLocaleString("ru-RU", {
            dateStyle: "medium",
            timeStyle: "short",
        });

    const buildWhatsAppUrl = (phoneNumber?: string | null) => {
        if (!phoneNumber) return null;
        const digits = phoneNumber.replace(/\D/g, "");
        return digits ? `https://wa.me/${digits}` : null;
    };

    const formatTariffPeriod = (period?: string) => {
        if (period === "day") return "1 день";
        if (period === "week") return "Неделя";
        if (period === "month") return "Месяц";
        return "Не указан";
    };

    const handlePasswordReset = async (e: React.FormEvent<HTMLFormElement>) => {
        e.preventDefault();
        setLoading(true);
        setErrorMsg("");
        setSuccessMsg("");

        try {
            if (!userEmail) throw new Error("Email не найден");
            await api.resetPassword(userEmail);
            setSuccessMsg("Ссылка для сброса пароля отправлена на ваш email.");
        } catch (err: any) {
            setErrorMsg(err.message || "Ошибка отправки письма");
        } finally {
            setLoading(false);
        }
    };

    return (
        <Dialog open={isOpen} onOpenChange={(open) => !open && onClose()}>
            <DialogContent className="sm:max-w-5xl max-h-[90vh] overflow-hidden">
                <DialogHeader>
                    <DialogTitle>Личный кабинет</DialogTitle>
                    <DialogDescription>
                        Управление вашим профилем, подпиской и историей открытых кандидатов.
                    </DialogDescription>
                </DialogHeader>

                <div className="grid gap-6 overflow-y-auto py-4 lg:grid-cols-[320px_minmax(0,1fr)]">
                    <div className="space-y-6">
                        <div className="rounded-lg border bg-muted/30 p-4">
                            <h4 className="mb-3 flex items-center gap-2 text-sm font-semibold">
                                🎫 Ваша подписка
                            </h4>
                            {subLoading ? (
                                <div className="h-10 animate-pulse rounded bg-muted"></div>
                            ) : subscription ? (
                                <div className="space-y-2">
                                    <div className="flex justify-between text-sm">
                                        <span className="text-muted-foreground">Тариф:</span>
                                        <span className="font-medium text-primary">
                                            {subscription.tariff_plans?.name || "Активный"}
                                        </span>
                                    </div>
                                    <div className="flex justify-between text-sm">
                                        <span className="text-muted-foreground">Период:</span>
                                        <span className="font-medium">
                                            {formatTariffPeriod(subscription.tariff_plans?.period)}
                                        </span>
                                    </div>
                                    <div className="flex justify-between text-sm">
                                        <span className="text-muted-foreground">Осталось просмотров:</span>
                                        <span className="font-medium">{subscription.cards_remaining}</span>
                                    </div>
                                    {subscription.daily_limit ? (
                                        <div className="flex justify-between text-sm">
                                            <span className="text-muted-foreground">Осталось на сегодня:</span>
                                            <span className="font-medium">
                                                {subscription.daily_views_remaining ?? 0} из {subscription.daily_limit}
                                            </span>
                                        </div>
                                    ) : null}
                                    <div className="flex justify-between text-sm">
                                        <span className="text-muted-foreground">Действует до:</span>
                                        <span className="font-medium">
                                            {new Date(subscription.expires_at).toLocaleDateString()}
                                        </span>
                                    </div>
                                </div>
                            ) : (
                                <p className="text-sm text-balance text-muted-foreground">
                                    У вас пока нет активной подписки. Перейдите в раздел "Тарифы", чтобы начать поиск кандидатов.
                                </p>
                            )}
                        </div>

                        <form onSubmit={handlePasswordReset} className="grid gap-4 rounded-lg border p-4">
                            <div className="grid gap-2">
                                <Label htmlFor="email" className="text-sm font-semibold text-muted-foreground">
                                    Ваш Email
                                </Label>
                                <Input
                                    id="email"
                                    disabled
                                    value={userEmail || "Неизвестно"}
                                    className="bg-muted"
                                />
                            </div>

                            <div className="pt-2">
                                <h4 className="mb-2 text-sm font-semibold">Безопасность</h4>
                                <p className="mb-4 text-sm text-muted-foreground">
                                    Сброс пароля отправит ссылку на вашу почту.
                                </p>

                                {successMsg && <p className="mb-2 text-sm text-green-600">{successMsg}</p>}
                                {errorMsg && <p className="mb-2 text-sm text-destructive">{errorMsg}</p>}
                            </div>

                            <DialogFooter className="px-0 pt-2">
                                <Button type="submit" className="w-full" variant="outline" disabled={loading || !userEmail}>
                                    {loading ? "Отправка..." : "Сбросить пароль"}
                                </Button>
                            </DialogFooter>
                        </form>
                    </div>

                    <div className="rounded-lg border p-4">
                        <div className="mb-4 flex items-center justify-between gap-4">
                            <div>
                                <h4 className="text-sm font-semibold">История открытых кандидатов</h4>
                                <p className="text-sm text-muted-foreground">
                                    Здесь сохраняются все кандидаты, которых вы уже открывали.
                                </p>
                            </div>
                            <div className="rounded-full bg-primary/10 px-3 py-1 text-sm font-medium text-primary">
                                {viewedHistory.length}
                            </div>
                        </div>

                        {historyLoading ? (
                            <div className="space-y-3">
                                <div className="h-24 animate-pulse rounded-xl bg-muted" />
                                <div className="h-24 animate-pulse rounded-xl bg-muted" />
                                <div className="h-24 animate-pulse rounded-xl bg-muted" />
                            </div>
                        ) : viewedHistory.length === 0 ? (
                            <div className="flex min-h-[240px] items-center justify-center rounded-2xl border border-dashed bg-muted/20 px-6 text-center text-sm text-muted-foreground">
                                Пока нет открытых кандидатов. Когда откроете первую анкету, история появится здесь.
                            </div>
                        ) : (
                            <div className="max-h-[58vh] space-y-3 overflow-y-auto pr-1">
                                {viewedHistory.map((employee) => (
                                    <div key={employee.id} className="rounded-2xl border bg-background p-3 sm:p-4">
                                        {(() => {
                                            const telegramUsername = employee.telegram_username?.replace(/^@/, "") || null;
                                            const telegramLink = telegramUsername
                                                ? `https://t.me/${telegramUsername}`
                                                : employee.telegram_id
                                                    ? `tg://user?id=${employee.telegram_id}`
                                                    : null;
                                            const whatsappUrl = employee.has_whatsapp ? buildWhatsAppUrl(employee.phone_number) : null;

                                            return (
                                                <>
                                                    <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
                                                        <div>
                                                            <div className="flex items-center gap-2">
                                                                <h5 className="font-semibold">{employee.full_name}</h5>
                                                                <VerificationBadge
                                                                    status={employee.verification_status}
                                                                    isVerified={employee.is_verified}
                                                                />
                                                            </div>
                                                            <p className="mt-1 text-sm text-muted-foreground">
                                                                {[employee.specializations, employee.district].filter(Boolean).join(" • ")}
                                                            </p>
                                                        </div>
                                                        <p className="text-xs text-muted-foreground">
                                                            Открыт: {formatViewedAt(employee.viewed_at)}
                                                        </p>
                                                    </div>

                                                    <div className="mt-3 grid gap-2 text-sm text-muted-foreground sm:grid-cols-2">
                                                        <p>Возраст: <span className="text-foreground">{employee.age ?? "Не указано"}</span></p>
                                                        <p>Пол: <span className="text-foreground">{employee.gender || "Не указано"}</span></p>
                                                        <p>Опыт: <span className="text-foreground">{employee.experience || "Не указано"}</span></p>
                                                        <p>Opus: <span className="text-foreground">{employee.opus_experience || "Не указано"}</span></p>
                                                        <p>Telegram: <span className="text-foreground">{telegramUsername ? `@${telegramUsername}` : "Не указан"}</span></p>
                                                        <p>Номер: <span className="text-foreground">{employee.phone_number || "Не указан"}</span></p>
                                                    </div>

                                                    <div className="mt-4 flex flex-col sm:flex-row sm:flex-wrap items-stretch sm:items-center gap-2 sm:gap-3">
                                                        {telegramLink ? (
                                                            <Button asChild size="sm" variant="outline" className="w-full sm:w-auto">
                                                                <a href={telegramLink} target="_blank" rel="noreferrer">
                                                                    Telegram
                                                                </a>
                                                            </Button>
                                                        ) : null}
                                                        {whatsappUrl ? (
                                                            <Button asChild size="sm" className="w-full sm:w-auto">
                                                                <a href={whatsappUrl} target="_blank" rel="noreferrer">
                                                                    WhatsApp
                                                                </a>
                                                            </Button>
                                                        ) : employee.phone_number ? (
                                                            <span className="text-xs text-muted-foreground">
                                                                У кандидата нет WhatsApp. Доступен обычный номер: {employee.phone_number}
                                                            </span>
                                                        ) : (
                                                            <span className="text-xs text-muted-foreground">
                                                                Контакты не указаны
                                                            </span>
                                                        )}
                                                    </div>
                                                </>
                                            );
                                        })()}
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>
                </div>
            </DialogContent>
        </Dialog>
    );
}
