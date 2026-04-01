import {
    BadgeCheck,
    BriefcaseBusiness,
    Clock3,
    MessageCircleMore,
    Phone,
    ShieldCheck,
    Smartphone,
    Send,
    UserRound,
} from "lucide-react";

import { Button } from "@/components/ui/button";
import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogHeader,
    DialogTitle,
} from "@/components/ui/dialog";
import { getPhotoUrl, type EmployeeCard, type EmployeeFullProfile } from "@/lib/api";

interface EmployeeDetailsDialogProps {
    open: boolean;
    onOpenChange: (open: boolean) => void;
    employee: EmployeeCard | null;
    unlockedProfile?: EmployeeFullProfile | null;
    isAuthenticated: boolean;
    isUnlocking: boolean;
    isViewed: boolean;
    remainingCards: number | null;
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
    unlockError,
    onRequestLogin,
    onUnlock,
}: EmployeeDetailsDialogProps) {
    if (!employee) {
        return null;
    }

    const _telegramIdFull = unlockedProfile?.telegram_id ?? null;
    const photoTelegramId = unlockedProfile?.telegram_id ?? employee.telegram_id ?? null;
    // Используем telegramUsername или telegramId только из ПОЛНОГО профиля для связи
    const telegramUsername = unlockedProfile?.telegram_username?.replace(/^@/, "") || null;
    const telegramLink = telegramUsername
        ? `https://t.me/${telegramUsername}`
        : _telegramIdFull
            ? `tg://user?id=${_telegramIdFull}`
            : null;
    const whatsappUrl = unlockedProfile?.has_whatsapp ? buildWhatsAppUrl(unlockedProfile.phone_number) : null;
    const cardsInfo = isViewed
        ? "Контакт уже был открыт раньше и повторно не списывается."
        : remainingCards === null
            ? "Тариф пока не активирован"
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
            <DialogContent className="sm:max-w-3xl w-[95vw] sm:w-full p-0 overflow-hidden border shadow-xl rounded-xl bg-background">
                <DialogHeader className="px-4 pt-6 pb-3 sm:px-8 sm:pt-8 sm:pb-4 relative z-10 border-b border-border/40 bg-muted/10">
                    <div className="flex items-start justify-between gap-4">
                        <div className="flex items-center gap-4">
                            {photoTelegramId ? (
                                <div className="relative h-16 w-16 sm:h-20 sm:w-20 overflow-hidden rounded-full border-2 border-primary/20 bg-muted shrink-0 shadow-sm">
                                    <img
                                        src={getPhotoUrl(photoTelegramId)}
                                        alt={employee.full_name}
                                        className="h-full w-full object-cover"
                                        onError={(e) => {
                                            (e.currentTarget.parentElement as HTMLElement).innerHTML = `<div class="flex h-full w-full items-center justify-center text-muted-foreground"><svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="opacity-30"><circle cx="12" cy="8" r="5"/><path d="M20 21a8 8 0 0 0-16 0"/></svg></div>`
                                        }}
                                    />
                                </div>
                            ) : (
                                <div className="flex h-16 w-16 sm:h-20 sm:w-20 items-center justify-center rounded-full border-2 border-primary/20 bg-muted text-muted-foreground shrink-0 shadow-sm">
                                    <UserRound className="h-8 w-8 sm:h-10 sm:w-10 opacity-30" />
                                </div>
                            )}
                            <div>
                                <DialogTitle className="flex items-center gap-2 text-2xl sm:text-3xl font-bold tracking-tight">
                                    {employee.full_name}
                                    {employee.is_verified ? <BadgeCheck className="h-6 w-6 text-emerald-500" /> : null}
                                </DialogTitle>
                                <DialogDescription className="mt-2 text-base font-medium text-primary/80">
                                    {employee.specializations || "Специализация уточняется"}
                                </DialogDescription>
                            </div>
                        </div>
                    </div>
                </DialogHeader>

                <div className="px-4 py-4 sm:px-8 sm:py-6 space-y-5 sm:space-y-8 relative z-10 max-h-[85vh] sm:max-h-[75vh] overflow-y-auto">

                    <div className="grid gap-3 sm:gap-4 sm:grid-cols-3">
                        <div className="rounded-xl border border-border/50 bg-card p-4 sm:p-5 shadow-sm">
                            <p className="text-[10px] uppercase tracking-[0.2em] font-semibold text-muted-foreground">Возраст</p>
                            <p className="mt-2 text-2xl font-bold">{displayValue(employee.age)}</p>
                        </div>
                        <div className="rounded-xl border border-border/50 bg-card p-4 sm:p-5 shadow-sm">
                            <p className="text-[10px] uppercase tracking-[0.2em] font-semibold text-muted-foreground">Пол</p>
                            <p className="mt-2 text-2xl font-bold">{displayValue(employee.gender)}</p>
                        </div>
                        <div className="rounded-xl border border-border/50 bg-card p-4 sm:p-5 shadow-sm">
                            <p className="text-[10px] uppercase tracking-[0.2em] font-semibold text-muted-foreground">Район</p>
                            <p className="mt-2 text-2xl font-bold truncate">{displayValue(employee.district)}</p>
                        </div>
                    </div>

                    <div className="grid gap-4 sm:grid-cols-2">
                        <div className="rounded-xl border border-border/50 bg-card p-4 sm:p-5 shadow-sm">
                            <div className="mb-3 flex items-center gap-2 text-sm font-semibold">
                                <BriefcaseBusiness className="h-4 w-4 text-primary" />
                                Профессия
                            </div>
                            <p className="text-sm leading-6 text-muted-foreground">
                                {displayValue(employee.specializations)}
                            </p>
                        </div>

                        <div className="rounded-xl border border-border/50 bg-card p-4 sm:p-5 shadow-sm">
                            <div className="mb-3 flex items-center gap-2 text-sm font-semibold">
                                <ShieldCheck className="h-4 w-4 text-primary" />
                                Статус в базе
                            </div>
                            <p className="text-sm leading-6 text-muted-foreground">
                                {employee.is_verified ? "Проверенный сотрудник" : "Ожидает проверки"}
                            </p>
                        </div>

                        <div className="rounded-xl border border-border/50 bg-card p-4 sm:p-5 shadow-sm">
                            <div className="mb-3 flex items-center gap-2 text-sm font-semibold">
                                <UserRound className="h-4 w-4 text-primary" />
                                Опыт работы
                            </div>
                            <p className="text-sm leading-6 text-muted-foreground">
                                {displayValue(employee.experience)}
                            </p>
                        </div>

                        <div className="rounded-xl border border-border/50 bg-card p-4 sm:p-5 shadow-sm">
                            <div className="mb-3 flex items-center gap-2 text-sm font-semibold">
                                <Clock3 className="h-4 w-4 text-primary" />
                                Занятость
                            </div>
                            <p className="text-sm leading-6 text-muted-foreground">
                                {displayValue(unlockedProfile?.employment_type)}
                            </p>
                        </div>

                        <div className="rounded-xl border border-border/50 bg-card p-4 sm:p-5 shadow-sm">
                            <div className="mb-3 flex items-center gap-2 text-sm font-semibold">
                                <Clock3 className="h-4 w-4 text-primary" />
                                Готовность к выходным
                            </div>
                            <p className="text-sm leading-6 text-muted-foreground">
                                {displayYesNo(unlockedProfile?.ready_for_weekends)}
                            </p>
                        </div>

                        <div className="rounded-xl border border-border/50 bg-card p-4 sm:p-5 shadow-sm">
                            <div className="mb-3 flex items-center gap-2 text-sm font-semibold">
                                <ShieldCheck className="h-4 w-4 text-primary" />
                                Рекомендации
                            </div>
                            <p className="text-sm leading-6 text-muted-foreground">
                                {displayYesNo(unlockedProfile?.has_recommendations)}
                            </p>
                        </div>

                        <div className="rounded-xl border border-border/50 bg-card p-4 sm:p-5 sm:col-span-2 shadow-sm">
                            <div className="mb-3 flex items-center gap-2 text-sm font-semibold">
                                <UserRound className="h-4 w-4 text-primary" />
                                О себе
                            </div>
                            <p className="text-sm leading-6 text-muted-foreground">
                                {displayValue(unlockedProfile?.about_me)}
                            </p>
                        </div>
                    </div>

                    <div className="rounded-xl border border-primary/20 bg-primary/5 p-6 shadow-sm">
                        <div className="flex flex-col gap-5 sm:flex-row sm:items-center sm:justify-between">
                            <div className="space-y-3">
                                <div className="flex items-center gap-2 text-base font-bold text-foreground">
                                    <MessageCircleMore className="h-5 w-5 text-primary" />
                                    Контакты и связь
                                </div>
                                {unlockedProfile ? (
                                    <div className="space-y-2 text-sm text-muted-foreground">
                                        <p className="font-medium text-primary">Контакты открыты. Можно написать сотруднику напрямую.</p>
                                        <div className="space-y-1.5 text-xs">
                                            <p><strong className="text-foreground font-medium">Telegram:</strong> {telegramUsername ? `@${telegramUsername}` : _telegramIdFull ? `ID ${_telegramIdFull}` : "Не указан"}</p>
                                            <p><strong className="text-foreground font-medium">Номер:</strong> {displayValue(unlockedProfile?.phone_number)}</p>
                                            <p>
                                                <strong className="text-foreground font-medium">WhatsApp:</strong> {unlockedProfile?.has_whatsapp ? "Есть" : "Нет, только обычный номер"}
                                            </p>
                                        </div>
                                    </div>
                                ) : (
                                    <div className="space-y-1.5 text-sm text-muted-foreground">
                                        <p>Часть данных анкеты закрыта. Для связи необходимо открыть контакт.</p>
                                        <p className="text-xs font-semibold text-primary">{cardsInfo}</p>
                                    </div>
                                )}
                            </div>

                            {telegramLink || unlockedProfile?.phone_number ? (
                                <div className="flex flex-col gap-3 min-w-0 sm:min-w-[240px] w-full sm:w-auto">
                                    {telegramLink ? (
                                        <Button asChild className="w-full h-11 rounded-lg shadow-md" variant="default">
                                            <a href={telegramLink} target="_blank" rel="noreferrer">
                                                <Send className="mr-2 h-4 w-4" />
                                                Написать в Telegram
                                            </a>
                                        </Button>
                                    ) : null}
                                    {whatsappUrl ? (
                                        <Button asChild className="w-full h-11 rounded-lg bg-[#25D366] hover:bg-[#20BE5A] text-white shadow-md">
                                            <a href={whatsappUrl} target="_blank" rel="noreferrer">
                                                <Smartphone className="mr-2 h-4 w-4" />
                                                Написать в WhatsApp
                                            </a>
                                        </Button>
                                    ) : unlockedProfile?.phone_number ? (
                                        <div className="rounded-lg border border-border/50 bg-card px-4 py-3 text-sm text-foreground shadow-sm">
                                            <div className="flex items-center justify-center gap-2 font-bold">
                                                <Phone className="h-4 w-4 text-primary" />
                                                {unlockedProfile.phone_number}
                                            </div>
                                            <p className="mt-1.5 text-center text-xs text-muted-foreground leading-tight">
                                                У сотрудника нет WhatsApp. Только звонки/смс.
                                            </p>
                                        </div>
                                    ) : null}
                                </div>
                            ) : (
                                <Button
                                    onClick={handlePrimaryAction}
                                    className="w-full sm:min-w-[240px] h-11 sm:h-12 text-xs sm:text-sm font-semibold rounded-lg shadow-md bg-foreground text-background hover:bg-foreground/90"
                                    disabled={isUnlocking}
                                >
                                    {isUnlocking ? "Открываем..." : isViewed ? "Открыть снова" : "Открыть контакт и связаться"}
                                </Button>
                            )}
                        </div>

                        {!isAuthenticated ? (
                            <p className="mt-4 text-xs font-medium text-center text-muted-foreground bg-muted/50 py-2 rounded-lg">
                                Чтобы открыть контакт сотрудника, необходимо авторизоваться на платформе.
                            </p>
                        ) : null}

                        {unlockError ? (
                            <div className="mt-4 p-3 bg-destructive/10 border border-destructive/20 rounded-xl">
                                <p className="text-sm font-medium text-destructive text-center">{unlockError}</p>
                            </div>
                        ) : null}
                    </div>
                </div>
            </DialogContent>
        </Dialog>
    );
}
