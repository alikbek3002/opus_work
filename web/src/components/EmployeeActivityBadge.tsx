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
    label: string;
    className: string;
    icon: LucideIcon;
}

const metaByEmploymentType: Record<string, Record<ActivitySignal, ActivityMeta>> = {
    "Подработки": {
        high: {
            label: "Готов(а) выйти сегодня или завтра",
            className: "text-emerald-700 bg-emerald-500/10 border-emerald-500/20",
            icon: Zap,
        },
        medium: {
            label: "Может выйти в ближайшие дни",
            className: "text-sky-700 bg-sky-500/10 border-sky-500/20",
            icon: CalendarClock,
        },
        low: {
            label: "Пока рассматривает выборочно",
            className: "text-slate-700 bg-slate-500/10 border-slate-500/20",
            icon: BriefcaseBusiness,
        },
    },
    "Постоянная работа": {
        high: {
            label: "Активно ищет работу",
            className: "text-emerald-700 bg-emerald-500/10 border-emerald-500/20",
            icon: Zap,
        },
        medium: {
            label: "Рассматривает хорошие предложения",
            className: "text-sky-700 bg-sky-500/10 border-sky-500/20",
            icon: CalendarClock,
        },
        low: {
            label: "Ищет без спешки",
            className: "text-slate-700 bg-slate-500/10 border-slate-500/20",
            icon: BriefcaseBusiness,
        },
    },
};

function resolveActivityEmploymentType(employmentType?: string | null) {
    if (!employmentType) return null;

    const normalizedValues = employmentType
        .split(",")
        .map((value) => value.trim().toLowerCase())
        .filter(Boolean);

    if (normalizedValues.some((value) => value.includes("постоян"))) {
        return "Постоянная работа";
    }
    if (normalizedValues.some((value) => value.includes("подработ"))) {
        return "Подработки";
    }
    if (normalizedValues.some((value) => value.includes("сезон"))) {
        return "Подработки";
    }

    return null;
}

function getActivityMeta(employmentType?: string | null, activitySignal?: ActivitySignal | null): ActivityMeta | null {
    if (!employmentType || !activitySignal) return null;
    const resolvedEmploymentType = resolveActivityEmploymentType(employmentType);
    if (!resolvedEmploymentType) return null;
    return metaByEmploymentType[resolvedEmploymentType]?.[activitySignal] ?? null;
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

    if (!meta) {
        return null; // Return null if it's a placeholder or missing data
    }

    const Icon = meta.icon;
    const updatedAtText = formatUpdatedAt(activitySignalUpdatedAt);

    if (compact) {
        return (
            <div className={cn("inline-flex items-center gap-1.5 rounded-lg border px-2.5 py-1 w-fit", meta.className, className)}>
                <Icon className="h-3.5 w-3.5 shrink-0" />
                <span className="truncate text-[13px] font-medium leading-none">{meta.label}</span>
            </div>
        );
    }

    return (
        <div className={cn("inline-flex items-center gap-2 rounded-xl border px-3.5 py-2 w-fit", meta.className, className)}>
            <Icon className="h-4 w-4 shrink-0" />
            <div className="flex flex-col min-w-0">
                <span className="text-sm font-semibold">{meta.label}</span>
                {updatedAtText && (
                    <span className="text-[11px] opacity-80 mt-0.5">Обновлено: {updatedAtText}</span>
                )}
            </div>
        </div>
    );
}
