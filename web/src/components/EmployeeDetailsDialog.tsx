import {
    BadgeCheck,
    MessageCircleMore,
    Phone,
    Send,
    Smartphone,
} from "lucide-react";

import { Button } from "@/components/ui/button";
import {
    Dialog,
    DialogContent,
    DialogHeader,
    DialogTitle,
} from "@/components/ui/dialog";
import { getPhotoUrl, type EmployeeCard, type EmployeeFullProfile } from "@/lib/api";
import EmployeeActivityBadge from "@/components/EmployeeActivityBadge";
import { getVerificationLabel, normalizeVerificationStatus } from "@/components/VerificationBadge";

interface EmployeeDetailsDialogProps {
    open: boolean;
    onOpenChange: (open: boolean) => void;
    employee: EmployeeCard | null;
    unlockedProfile?: EmployeeFullProfile | null;
    isAuthenticated: boolean;
    isUnlocking: boolean;
    isViewed: boolean;
    remainingCards: number | null;
    dailyRemaining?: number | null;
    dailyLimit?: number | null;
    unlockError?: string | null;
    onRequestLogin: () => void;
    onUnlock: (employeeId: string) => void | Promise<void>;
}

function displayValue(value?: string | number | null, fallback = "Не указано") {
    if (value === null || value === undefined || value === "") {
        return fallback;
    }
    return String(value);
}

function displayYesNo(value?: boolean | null) {
    if (value === null || value === undefined) return "Не указано";
    return value ? "Да" : "Нет";
}

function buildWhatsAppUrl(phoneNumber?: string | null) {
    if (!phoneNumber) return null;
    const digits = phoneNumber.replace(/\D/g, "");
    return digits ? `https://wa.me/${digits}` : null;
}

export default function EmployeeDetailsDialog({
    open,
    onOpenChange,
    employee,
    unlockedProfile,
    isAuthenticated,
    isUnlocking,
    isViewed,
    remainingCards,
    dailyRemaining,
    dailyLimit,
    unlockError,
    onRequestLogin,
    onUnlock,
}: EmployeeDetailsDialogProps) {
    if (!employee) {
        return null;
    }

    const _telegramIdFull = unlockedProfile?.telegram_id ?? null;
    const photoTelegramId = unlockedProfile?.telegram_id ?? employee.telegram_id ?? null;
    const telegramUsername = unlockedProfile?.telegram_username?.replace(/^@/, "") || null;
    const telegramLink = telegramUsername
        ? `https://t.me/${telegramUsername}`
        : _telegramIdFull
            ? `tg://user?id=${_telegramIdFull}`
            : null;
    const whatsappUrl = unlockedProfile?.has_whatsapp ? buildWhatsAppUrl(unlockedProfile.phone_number) : null;
    const verificationStatus = normalizeVerificationStatus(employee.verification_status, employee.is_verified);
    const activityEmploymentType = unlockedProfile?.employment_type ?? employee.employment_type;
    const activitySignal = unlockedProfile?.activity_signal ?? employee.activity_signal;
    const activitySignalUpdatedAt = unlockedProfile?.activity_signal_updated_at ?? employee.activity_signal_updated_at;
    const cardsInfo = isViewed
        ? "Контакт уже был открыт раньше и повторно не списывается."
        : remainingCards === null
            ? "Тариф пока не активирован"
            : dailyLimit
                ? `Осталось открытий: ${remainingCards}. На сегодня: ${dailyRemaining ?? 0} из ${dailyLimit}.`
                : `Осталось открытий: ${remainingCards}`;

    const handlePrimaryAction = () => {
        if (!isAuthenticated) {
            onRequestLogin();
            return;
        }
        void onUnlock(employee.id);
    };

    return (
        <Dialog open={open} onOpenChange={onOpenChange}>
            <DialogContent className="sm:max-w-3xl w-[95vw] sm:w-full p-0 overflow-hidden border-0 shadow-2xl rounded-2xl bg-background">
                <DialogHeader className="p-6 sm:p-8 border-b border-border/30 bg-muted/20 relative">
                    <div className="flex flex-col sm:flex-row items-start sm:items-center gap-5 sm:gap-6">
                        {photoTelegramId ? (
                            <img
                                src={getPhotoUrl(photoTelegramId)}
                                alt={employee.full_name}
                                className="h-16 w-16 sm:h-24 sm:w-24 object-cover rounded-full border-2 border-border/50 bg-background shadow-sm shrink-0"
                                onError={(e) => {
                                    (e.currentTarget.parentElement as HTMLElement).innerHTML = `<div class="flex h-16 w-16 sm:h-24 sm:w-24 items-center justify-center overflow-hidden bg-white p-3 rounded-full border-2 border-border/50"><img src="/logo.png" alt="Opus" class="h-full w-full object-contain" /></div>`
                                }}
                            />
                        ) : (
                            <div className="flex h-16 w-16 sm:h-24 sm:w-24 items-center justify-center rounded-full border-2 border-border/50 bg-white shrink-0 p-3 shadow-sm">
                                <img src="/logo.png" alt="Opus" className="h-full w-full object-contain" />
                            </div>
                        )}
                        <div className="space-y-1.5 w-full">
                            <DialogTitle className="flex flex-wrap items-center gap-2 text-2xl sm:text-3xl font-extrabold text-foreground leading-tight">
                                <span>{employee.full_name} — {employee.age || "?"} лет</span>
                                {employee.is_verified && <BadgeCheck className="h-6 w-6 text-emerald-500 shrink-0" />}
                            </DialogTitle>
                            <p className="text-lg font-medium text-primary">
                                {employee.specializations || "Специализация уточняется"}
                            </p>
                            <EmployeeActivityBadge
                                employmentType={activityEmploymentType}
                                activitySignal={activitySignal}
                                activitySignalUpdatedAt={activitySignalUpdatedAt}
                                compact
                            />
                        </div>
                    </div>
                </DialogHeader>

                <div className="px-6 py-6 sm:px-8 sm:py-8 max-h-[75vh] overflow-y-auto">
                    <div className="space-y-8">
                        <section>
                            <h4 className="text-sm font-semibold uppercase tracking-wider text-muted-foreground mb-4">Информация</h4>
                            <dl className="divide-y divide-border/40">
                                <div className="py-3 flex flex-col sm:grid sm:grid-cols-3 sm:gap-4">
                                    <dt className="text-sm font-medium text-muted-foreground">Пол</dt>
                                    <dd className="mt-1 text-sm text-foreground sm:col-span-2 sm:mt-0 font-medium">{displayValue(employee.gender)}</dd>
                                </div>
                                <div className="py-3 flex flex-col sm:grid sm:grid-cols-3 sm:gap-4">
                                    <dt className="text-sm font-medium text-muted-foreground">Район</dt>
                                    <dd className="mt-1 text-sm text-foreground sm:col-span-2 sm:mt-0 font-medium">{displayValue(employee.district)}</dd>
                                </div>
                                <div className="py-3 flex flex-col sm:grid sm:grid-cols-3 sm:gap-4">
                                    <dt className="text-sm font-medium text-muted-foreground">Опыт работы</dt>
                                    <dd className="mt-1 text-sm text-foreground sm:col-span-2 sm:mt-0 font-medium">{displayValue(employee.experience)}</dd>
                                </div>
                                <div className="py-3 flex flex-col sm:grid sm:grid-cols-3 sm:gap-4">
                                    <dt className="text-sm font-medium text-muted-foreground">О себе</dt>
                                    <dd className="mt-1 text-sm text-foreground sm:col-span-2 sm:mt-0 whitespace-pre-wrap leading-relaxed">{displayValue(unlockedProfile?.about_me)}</dd>
                                </div>
                            </dl>
                        </section>

                        <section>
                            <h4 className="text-sm font-semibold uppercase tracking-wider text-muted-foreground mb-4">Детали занятости</h4>
                            <dl className="divide-y divide-border/40">
                                <div className="py-3 flex flex-col sm:grid sm:grid-cols-3 sm:gap-4">
                                    <dt className="text-sm font-medium text-muted-foreground">Занятость</dt>
                                    <dd className="mt-1 text-sm text-foreground sm:col-span-2 sm:mt-0">{displayValue(activityEmploymentType)}</dd>
                                </div>
                                <div className="py-3 flex flex-col sm:grid sm:grid-cols-3 sm:gap-4">
                                    <dt className="text-sm font-medium text-muted-foreground">Готовность к выходным</dt>
                                    <dd className="mt-1 text-sm text-foreground sm:col-span-2 sm:mt-0">{displayYesNo(unlockedProfile?.ready_for_weekends)}</dd>
                                </div>
                                <div className="py-3 flex flex-col sm:grid sm:grid-cols-3 sm:gap-4">
                                    <dt className="text-sm font-medium text-muted-foreground">Рекомендации</dt>
                                    <dd className="mt-1 text-sm text-foreground sm:col-span-2 sm:mt-0">{displayYesNo(unlockedProfile?.has_recommendations)}</dd>
                                </div>
                            </dl>
                        </section>

                        <section className="rounded-xl border border-border/40 bg-muted/10 p-5 mt-4">
                            <h4 className="text-sm font-semibold text-foreground mb-2">Статус в базе</h4>
                            <div className="text-sm text-muted-foreground space-y-1">
                                <p>
                                    {verificationStatus === "verified"
                                        ? "Анкета полностью проверена и подтверждена нашими модераторами."
                                        : verificationStatus === "rejected"
                                            ? "Анкета не прошла проверку у модератора."
                                            : "Анкета находится на этапе ручной проверки."}
                                </p>
                                {unlockedProfile?.verification_rejected_reason ? (
                                    <p className="text-xs text-destructive pt-1">
                                        Причина: {unlockedProfile.verification_rejected_reason}
                                    </p>
                                ) : null}
                            </div>
                        </section>
                    </div>

                    <div className="mt-8 rounded-xl border border-primary/20 bg-primary/5 p-6 sm:p-8">
                        <div className="flex flex-col gap-6 sm:flex-row sm:items-center sm:justify-between">
                            <div className="space-y-4 max-w-md">
                                <div className="flex items-center gap-2 text-lg font-bold text-foreground">
                                    <MessageCircleMore className="h-5 w-5 text-primary" />
                                    Контакты и связь
                                </div>
                                {unlockedProfile ? (
                                    <div className="space-y-3">
                                        <p className="text-sm font-medium text-primary">Вы открыли контакт. Можно писать кандидату.</p>
                                        <div className="space-y-2 text-sm">
                                            <div className="flex items-center gap-2">
                                                <span className="text-muted-foreground w-20">Telegram:</span>
                                                <span className="font-semibold text-foreground">{telegramUsername ? `@${telegramUsername}` : _telegramIdFull ? `ID ${_telegramIdFull}` : "Не указан"}</span>
                                            </div>
                                            <div className="flex items-center gap-2">
                                                <span className="text-muted-foreground w-20">Телефон:</span>
                                                <span className="font-semibold text-foreground">{displayValue(unlockedProfile?.phone_number)}</span>
                                            </div>
                                            <div className="flex items-center gap-2">
                                                <span className="text-muted-foreground w-20">WhatsApp:</span>
                                                <span className="font-semibold text-foreground">{unlockedProfile?.has_whatsapp ? "Доступен" : "Отсутствует"}</span>
                                            </div>
                                        </div>
                                    </div>
                                ) : (
                                    <div className="space-y-2 text-sm text-muted-foreground">
                                        <p>Часть данных анкеты закрыта. Для связи необходимо открыть контакт кандидата.</p>
                                        <p className="font-medium text-primary bg-primary/10 inline-block px-3 py-1 rounded-md">{cardsInfo}</p>
                                    </div>
                                )}
                            </div>

                            <div className="shrink-0 w-full sm:w-auto">
                                {telegramLink || unlockedProfile?.phone_number ? (
                                    <div className="flex flex-col gap-3 min-w-0 sm:min-w-[220px]">
                                        {telegramLink ? (
                                            <Button asChild className="w-full h-11 rounded-xl shadow-sm text-sm" variant="default">
                                                <a href={telegramLink} target="_blank" rel="noreferrer">
                                                    <Send className="mr-2 h-4 w-4" />
                                                    Написать в Telegram
                                                </a>
                                            </Button>
                                        ) : null}
                                        {whatsappUrl ? (
                                            <Button asChild className="w-full h-11 rounded-xl bg-[#25D366] hover:bg-[#20BE5A] text-white shadow-sm text-sm">
                                                <a href={whatsappUrl} target="_blank" rel="noreferrer">
                                                    <Smartphone className="mr-2 h-4 w-4" />
                                                    Написать в WhatsApp
                                                </a>
                                            </Button>
                                        ) : unlockedProfile?.phone_number ? (
                                            <div className="rounded-xl border border-border/50 bg-card px-4 py-3 shadow-sm text-center">
                                                <div className="flex items-center justify-center gap-2 font-bold text-base">
                                                    <Phone className="h-4 w-4 text-primary" />
                                                    {unlockedProfile.phone_number}
                                                </div>
                                                <p className="mt-1 text-xs text-muted-foreground">WhatsApp отсутствует</p>
                                            </div>
                                        ) : null}
                                    </div>
                                ) : (
                                    <Button
                                        onClick={handlePrimaryAction}
                                        className="w-full sm:min-w-[220px] h-12 text-sm font-bold rounded-xl shadow-md bg-foreground text-background hover:bg-foreground/90 transition-all active:scale-[0.98]"
                                        disabled={isUnlocking}
                                    >
                                        {isUnlocking ? "Открываем..." : isViewed ? "Открыть контакт" : "Открыть контакт"}
                                    </Button>
                                )}
                            </div>
                        </div>

                        {!isAuthenticated ? (
                            <p className="mt-5 text-sm font-medium text-center text-muted-foreground bg-muted/60 py-2.5 rounded-lg border border-border/40">
                                Для просмотра контактов авторизуйтесь.
                            </p>
                        ) : null}

                        {unlockError ? (
                            <div className="mt-5 p-3 sm:p-4 bg-destructive/10 border border-destructive/20 rounded-xl">
                                <p className="text-sm font-medium text-destructive text-center">{unlockError}</p>
                            </div>
                        ) : null}
                    </div>
                </div>
            </DialogContent>
        </Dialog>
    );
}
