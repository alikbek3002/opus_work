import { BriefcaseBusiness, CalendarClock, Zap, type LucideIcon } from "lucide-react";

import { type ActivitySignal } from "@/lib/api";
import { cn } from "@/lib/utils";

interface EmployeeActivityBadgeProps {
    employmentType?: string | null;
    activitySignal?: ActivitySignal | null;
    activitySignalUpdatedAt?: string | null;
    className?: string;
    compact?: boolean;
}

interface ActivityMeta {
    title: string;
    label: string;
    className: string;
    icon: LucideIcon;
}

const metaByEmploymentType: Record<string, Record<ActivitySignal, ActivityMeta>> = {
    "Подработка": {
        high: {
            title: "Готовность к смене",
            label: "Готов(а) выйти сегодня или завтра",
            className: "border-emerald-500/20 bg-emerald-500/10 text-emerald-700",
            icon: Zap,
        },
        medium: {
            title: "Готовность к смене",
            label: "Может выйти в ближайшие дни",
            className: "border-sky-500/20 bg-sky-500/10 text-sky-700",
            icon: CalendarClock,
        },
        low: {
            title: "Готовность к смене",
            label: "Пока рассматривает выборочно",
            className: "border-slate-500/20 bg-slate-500/10 text-slate-700",
            icon: BriefcaseBusiness,
        },
    },
    "Полная занятость": {
        high: {
            title: "Поиск работы",
            label: "Активно ищет работу",
            className: "border-emerald-500/20 bg-emerald-500/10 text-emerald-700",
            icon: Zap,
        },
        medium: {
            title: "Поиск работы",
            label: "Рассматривает хорошие предложения",
            className: "border-sky-500/20 bg-sky-500/10 text-sky-700",
            icon: CalendarClock,
        },
        low: {
            title: "Поиск работы",
            label: "Ищет без спешки",
            className: "border-slate-500/20 bg-slate-500/10 text-slate-700",
            icon: BriefcaseBusiness,
        },
    },
};

function getActivityMeta(employmentType?: string | null, activitySignal?: ActivitySignal | null): ActivityMeta | null {
    if (!employmentType || !activitySignal) return null;
    return metaByEmploymentType[employmentType]?.[activitySignal] ?? null;
}

function getActivityPlaceholder(employmentType?: string | null): { title: string; label: string } | null {
    if (employmentType === "Подработка") {
        return {
            title: "Готовность к смене",
            label: "Статус ещё не обновлялся",
        };
    }

    if (employmentType === "Полная занятость") {
        return {
            title: "Поиск работы",
            label: "Статус ещё не обновлялся",
        };
    }

    return null;
}

export function getEmployeeActivitySummary(
    employmentType?: string | null,
    activitySignal?: ActivitySignal | null
) {
    return getActivityMeta(employmentType, activitySignal) ?? getActivityPlaceholder(employmentType);
}

function formatUpdatedAt(value?: string | null) {
    if (!value) return null;
    return new Date(value).toLocaleString("ru-RU", {
        dateStyle: "short",
        timeStyle: "short",
    });
}

export default function EmployeeActivityBadge({
    employmentType,
    activitySignal,
    activitySignalUpdatedAt,
    className,
    compact = false,
}: EmployeeActivityBadgeProps) {
    const meta = getActivityMeta(employmentType, activitySignal);
    const placeholder = getActivityPlaceholder(employmentType);

    if (!meta && !placeholder) {
        return null;
    }

    if (!meta && placeholder) {
        return (
            <div className={cn("rounded-xl border border-dashed border-border/60 bg-muted/30 px-3 py-2", className)}>
                <p className="text-[11px] font-semibold uppercase tracking-[0.14em] text-muted-foreground">
                    {placeholder.title}
                </p>
                <p className="mt-1 text-sm text-muted-foreground">{placeholder.label}</p>
            </div>
        );
    }

    const Icon = meta!.icon;
    const updatedAtText = formatUpdatedAt(activitySignalUpdatedAt);

    if (compact) {
        return (
            <div className={cn("rounded-xl border px-3 py-2", meta!.className, className)}>
                <div className="flex items-center gap-2">
                    <Icon className="h-4 w-4 shrink-0" />
                    <div className="min-w-0">
                        <p className="text-[11px] font-semibold uppercase tracking-[0.12em]">{meta!.title}</p>
                        <p className="truncate text-sm font-medium">{meta!.label}</p>
                    </div>
                </div>
            </div>
        );
    }

    return (
        <div className={cn("rounded-xl border px-3 py-3", meta!.className, className)}>
            <div className="flex items-start gap-2.5">
                <Icon className="mt-0.5 h-4 w-4 shrink-0" />
                <div className="min-w-0">
                    <p className="text-[11px] font-semibold uppercase tracking-[0.14em]">{meta!.title}</p>
                    <p className="mt-1 text-sm font-semibold leading-5">{meta!.label}</p>
                    {updatedAtText ? (
                        <p className="mt-1 text-xs opacity-80">Обновлено: {updatedAtText}</p>
                    ) : null}
                </div>
            </div>
        </div>
    );
}
